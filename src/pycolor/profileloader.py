import json
from shutil import which

from .config import ConfigPropertyError
from .config.profile import Profile
from .printmsg import printwarn


PROF_IDX_SEP = ';'


class ProfileLoader:
    def __init__(self):
        self.profiles = []
        self.named_profiles = {}

        self.profile_default = Profile({
            'profile_name': 'none_found_default',
        }, loader=self)

    def load_file(self, fname):
        with open(fname, 'r') as file:
            profiles = self.parse_file(file)

        for prof in profiles:
            self.profiles.append(prof)
            if prof.profile_name is not None:
                if prof.profile_name in self.named_profiles:
                    printwarn('conflicting profiles with the name "%s"' % prof.profile_name)
                self.named_profiles[prof.profile_name] = prof

    def parse_file(self, file):
        config = json.loads(file.read())
        profiles = []

        for cfg in config.get('profiles', []):
            profiles.append(Profile(cfg, loader=self))

        return profiles

    def include_from_profile(self, patterns, from_profiles):
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

    def get_profile_by_name(self, name):
        profile = self.named_profiles.get(name)
        if profile is not None:
            return profile

        for prof in self.profiles:
            if prof.name == name:
                return prof
        return None

    def get_profile_by_command(self, command, args):
        matches = []

        for prof in self.profiles:
            if not any([
                prof.which,
                prof.name,
                prof.name_regex
            ]):
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

            if any([
                prof.name is not None and command != prof.name,
                prof.min_args is not None and prof.min_args > len(args),
                prof.max_args is not None and prof.max_args < len(args),
                prof.name_regex is not None and not prof.name_regex.fullmatch(command),
            ]):
                continue

            if not ProfileLoader.check_arg_patterns(
                args,
                prof.arg_patterns
            ):
                continue

            matches.append(prof)

        if len(matches) == 0:
            return None
        return matches[-1]

    def is_default_profile(self, profile):
        return all([
            profile == self.profile_default,
            profile.timestamp is False,
        ])

    @staticmethod
    def check_arg_patterns(args, arg_patterns):
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
                subcmds = ProfileLoader.get_subcommands(args)
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
    def get_subcommands(args):
        subcmds = []
        for arg in args:
            if arg == '--':
                break
            if arg[0] != '-':
                subcmds.append(arg)
        return subcmds
