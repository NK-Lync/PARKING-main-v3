class VehicleClassifier:

    CLASS_MAPPING = {
        "motorcycle": "Xe máy",
        "car": "Ô tô",
        "bus": "Ô tô",
        "truck": "Ô tô"
    }

    @classmethod
    def classify(cls, vehicle_class):

        return cls.CLASS_MAPPING.get(
            vehicle_class,
            "Không xác định"
        )