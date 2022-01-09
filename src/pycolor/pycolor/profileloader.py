import json
from shutil import which
import typing

from ..config import ConfigPropertyError
from ..config.argpattern import ArgPattern
from ..config.fromprofile import FromProfile
from ..config.pattern import Pattern
from ..config.profile import Profile
from ..utils.printmsg import printwarn

PROF_IDX_SEP = ';'

class ProfileLoader:
    def __init__(self):
        self.profiles: typing.List[Profile] = []
        self.named_profiles: typing.Dict[str, Profile] = {}

        self.profile_default: Profile = Profile({
            'profile_name': 'none_found_default',
        }, loader=self)

    def load_file(self, fname: str) -> None:
        """Loads profiles from JSON file

        Args:
            fname (str): Filename
        """
        with open(fname, 'r') as file:
            profiles = self._parse_file(file)

        for prof in profiles:
            self.profiles.append(prof)
            if prof.profile_name is not None:
                if prof.profile_name in self.named_profiles:
                    printwarn('conflicting profiles with the name "%s"' % prof.profile_name)
                self.named_profiles[prof.profile_name] = prof

    def _parse_file(self, file: typing.TextIO) -> typing.List[Profile]:
        """Returns profiles from JSON file

        Args:
            file (TextIO): JSON file

        Returns:
            list: List of profiles from file
        """
        config = json.loads(file.read())
        return [ Profile(cfg, loader=self) for cfg in config.get('profiles', []) ]

    def include_from_profile(self,
        patterns: typing.List[Pattern],
        from_profiles: typing.Iterable[FromProfile]
    ) -> None:
        """Add patterns from FromProfiles

        Args:
            patterns (list): Pattern list to add to
            from_profiles (Iterable): FromProfiles to include from
        """
        fidx = -1
        for fprof in from_profiles:
            fidx += 1
            if not fprof.enabled:
                continue

            fromprof = self.get_profile_by_name(fprof.name)
            if fromprof is None:
                raise ConfigPropertyError(
                    'from_profiles',
                    'profile "%s" was not found' % fprof.name
                )

            # pylint: disable=consider-using-enumerate
            for i in range(len(fromprof.loaded_patterns)):
                pat = fromprof.loaded_patterns[i]
                # it's ok to modify these without copying
                pat.from_profile_str = '%x%s%x' % (fidx, PROF_IDX_SEP, i)

            if fprof.order == 'before':
                orig_patterns = patterns.copy()
                patterns.clear()
                patterns.extend(fromprof.loaded_patterns)
                patterns.extend(orig_patterns)
            elif fprof.order == 'after':
                patterns.extend(fromprof.loaded_patterns)

    def get_profile_by_name(self, name: str) -> typing.Optional[Profile]:
        """Gets loaded profile by name

        Args:
            name (str): Name of profile

        Returns:
            Profile: Profile with name, or None if not found
        """
        profile = self.named_profiles.get(name)
        if profile is not None:
            return profile

        for prof in self.profiles:
            if prof.name == name:
                return prof
        return None

    def get_profile_by_command(self,
        command: str,
        args: typing.List[str]
    ) -> typing.Optional[Profile]:
        """Gets the loaded profile by command and its arguments

        Args:
            command (str): Command being run
            args (list): Command arguments

        Returns:
            Profile: Last matching loaded profile, or null if not found
        """
        matches = []

        for prof in self.profiles:
            if not any((
                prof.which,
                prof.name,
                prof.name_regex
            )):
                continue
            if not prof.enabled:
                continue

            if prof.which is not None:
                result = which(command)
                if result is None:
                    continue
                if prof.which_ignore_case:
                    if result.lower() != prof.which.lower():
                        continue
                else:
                    if result != prof.which:
                        continue

            if any((
                prof.name is not None and command != prof.name,
                prof.min_args is not None and prof.min_args > len(args),
                prof.max_args is not None and prof.max_args < len(args)
            )):
                continue
            if prof.name_regex is not None and not prof.name_regex.fullmatch(command):
                continue
            if not ProfileLoader.check_arg_patterns(args, prof.arg_patterns):
                continue

            matches.append(prof)

        return matches[-1] if len(matches) > 0 else None

    def is_default_profile(self, profile: Profile) -> bool:
        """Checks if the profile is the default profile

        Args:
            profile (Profile): Profile to check

        Returns:
            bool: Returns true if the profile is the default profile
        """
        return all((
            profile == self.profile_default,
            profile.timestamp is False,
        ))

    @staticmethod
    def check_arg_patterns(
        args: typing.List[str],
        arg_patterns: typing.Iterable[ArgPattern]
    ) -> bool:
        """Checks if the args match the argument patterns

        Args:
            args (list): Arguments to check
            arg_patterns (Iterable): Argument patterns the args must match

        Returns:
            bool: Returns true if the args match the argument patterns
        """
        default_match = True
        found_match = False

        for argpat in arg_patterns:
            if not argpat.enabled:
                continue

            matches = False
            if argpat.regex is not None:
                for idx in argpat.get_arg_range(len(args)):
                    if argpat.regex.fullmatch(args[idx]):
                        matches = True
                        break
            elif len(argpat.subcommand) != 0:
                subcommands = argpat.subcommand
                subcmds = ProfileLoader._get_subcommands(args)
                matches = len(subcmds) >= len(subcommands)
                if matches:
                    for idx in range(len(subcommands)): # pylint: disable=consider-using-enumerate
                        if subcommands[idx] is not None and subcommands[idx] != subcmds[idx]:
                            matches = False
                            break
            else:
                continue

            if matches:
                if argpat.match_not:
                    return False
                found_match = True
            else:
                if not argpat.match_not:
                    if not argpat.optional:
                        return False
                    default_match = False
        return default_match or found_match

    @staticmethod
    def _get_subcommands(args: typing.Iterable[str]) -> typing.List[str]:
        """Gets the subcommands of args (non-dashed arguments)

        Args:
            args (Iterable): Arguments

        Returns:
            list: Subcommands
        """
        subcmds = []
        for arg in args:
            if arg == '--':
                break
            if arg[0] != '-':
                subcmds.append(arg)
        return subcmds
