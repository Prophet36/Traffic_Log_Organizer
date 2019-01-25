class DataHandler:

    @staticmethod
    def convert_to_int(value):
        try:
            converted_value = int(value)
        except ValueError:
            return value
        else:
            return converted_value

    @staticmethod
    def convert_to_float(value):
        try:
            converted_value = float(value)
        except ValueError:
            return value
        else:
            return converted_value

    @staticmethod
    def convert_to_number(value):
        value = DataHandler.convert_to_float(value)
        value = DataHandler.convert_to_int(value)
        return value

    @staticmethod
    def convert_to_string(value):
        try:
            converted_value = str(value)
        except ValueError:
            return value
        else:
            return converted_value
