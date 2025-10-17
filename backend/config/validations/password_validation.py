import re
import re


class PasswordValidation:
    """Class for validating different kinds of password.
    Including kinds of password:
    SIMPLE_8 - Any password with 8 or more characters
    LETTER_AND_DIGIT_8 - Minimum 8 characters, at least 1 letter and 1 digit
    LETTER_DIGIT_UPPER_8 - Minimum 8 characters, at least 1 letter, 1 digit, and 1 uppercase
    STRONG_8 - Minimum 8 characters, at least 1 uppercase, 1 lowercase, 1 digit, and 1 special character
    """

    __PASSWORD_PATTERNS = {
        "SIMPLE_8": re.compile(r"^.{8,}$"),
        "LETTER_AND_DIGIT_8": re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$"),
        "LETTER_DIGIT_UPPER_8": re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$"),
        "STRONG_8": re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$"),
    }

    __PASSWORD_MESSAGES = {
        "SIMPLE_8": "Password must be at least 8 characters long.",
        "LETTER_AND_DIGIT_8": "Password must be at least 8 characters long and include at least one letter and one digit.",
        "LETTER_DIGIT_UPPER_8": "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit.",
        "STRONG_8": "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, one digit, and one special character.",
    }

    def __init__(self, password_mask: str):
        self._passwork_mask = self.__PASSWORD_PATTERNS.get(password_mask, None)
        if self._passwork_mask == None:
            self._passwork_mask = self.__PASSWORD_PATTERNS[
                self.__PASSWORD_PATTERNS.keys()[0]
            ]

    async def validate_password(self, password: str) -> tuple[bool, str]:
        """
        Validate password: at least 8 characters.
        """
        if not self._passwork_mask.match(password):
            return (False, self.__PASSWORD_MESSAGES[self._passwork_mask])
        return (True, "")
