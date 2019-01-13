class DataHandler:

    @staticmethod
    def convert_to_int(value):
        try:
            converted_value = int(value)
        except ValueError:
            return value
        else:
            return converted_value