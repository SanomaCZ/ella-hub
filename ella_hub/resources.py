from tastypie.resources import ModelResource


class ApiModelResource(ModelResource):
    def alter_list_data_to_serialize(self, request, data):
        """
        Returns only field `objects` with usefull data.
        """
        if isinstance(data, dict) and "objects" in data:
            return data["objects"]
