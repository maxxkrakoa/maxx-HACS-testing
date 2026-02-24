class A:
    def _is_token_valid(self, token: str) -> bool:
        self._tokens = {"a": "b"}
        if not self._tokens:
            return False
        match token:
            case "access_token":
                ts = 1
                return False
            case "refresh":
                ts = 1
                return False
        return True
print(A()._is_token_valid("refresh_token"))
