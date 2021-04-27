import json

from config.profile import Profile
from which import which


class ProfileLoader:
    def __init__(self):
        self.profiles = []
        self.named_profiles = {}

        self.color_aliases = {}

        self.profile_default = Profile({
            'profile_name': 'none_found_default',
        })

    def load_file(self, fname):
        with open(fname, 'r') as file:
            profiles = self.parse_file(file)

        for prof in profiles:
            self.profiles.append(prof)
            if prof.profile_name is not None:
                self.named_profiles[prof.profile_name] = prof

        for prof in profiles:
            self.include_from_profile(
                prof.patterns,
                prof.from_profiles
            )

    def parse_file(self, file):
        config = json.loads(file.read())
        profiles = []

        self.color_aliases.update(config.get('color_aliases', {}))

        for cfg in config.get('profiles', []):
            profiles.append(Profile(cfg))

        return profiles

    def include_from_profile(self, patterns, from_profiles):
        for fprof in from_profiles:
            if not fprof.enabled:
                continue

            fromprof = self.get_profile_by_name(fprof.name)
            if fprof.order == 'before':
                orig_patterns = patterns.copy()
                patterns.clear()
                patterns.extend(fromprof.patterns)
                patterns.extend(orig_patterns)
            elif fprof.order == 'after':
                patterns.extend(fromprof.patterns)

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

            if prof.which is not None:
                result = which(command)
                if result is not None and result.decode('utf-8') != prof.which:
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
                prof.arg_patterns,
                prof.all_args_must_match
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
            profile.less_output is False,
        ])

    @staticmethod
    def check_arg_patterns(args, arg_patterns, all_must_match=False):
        idx_matches = set()

        for argpat in arg_patterns:
            matches = False
            for idx in argpat.get_arg_range(len(args)):
                if argpat.regex.fullmatch(args[idx]):
                    if argpat.match_not:
                        return False
                    idx_matches.add(idx)
                    matches = True

            if not any([
                matches,
                argpat.match_not,
                argpat.optional
            ]):
                return False

        if all_must_match and len(idx_matches) != len(args):
            return False
        return True
