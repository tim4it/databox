from response.response_init import ResponseInit, ResponseUnit


class DeathRate(ResponseInit):

    def parse(self) -> ResponseUnit:
        return super()._get_birth_death_response_unit("D")
