import re
import re

from config.validations.password_validation import PasswordValidation


class Validation(PasswordValidation):
    """Class for validating different kinds of data."""

    def __init__(self):
        PasswordValidation.__init__(
            self, password_mask="SIMPLE_8"
        )  # Select the type of password validation
