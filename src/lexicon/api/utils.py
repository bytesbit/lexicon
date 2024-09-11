from typing import Dict, List, Optional, Union


def prep_response_data(
    data: Optional[Union[Dict, List]] = None,
    item: Optional[dict] = None,
    items: Optional[List[dict]] = None,
    success: bool = True,
) -> Dict[str, Union[bool, Dict[str, Union[Dict, List]]]]:
    """
    Prepares a success response data dictionary based on the provided parameters.

    Args:
        data (Optional[Union[Dict, List]]): General data object, either a dictionary or a list.
        item (Optional[dict]): Specific item object, expected to be a dictionary.
        items (Optional[List[dict]]): List of items, where each item is expected to be a dictionary.
        success (bool): Indicates whether the response is successful. Defaults to True.

    Returns:
        Dict[str, Union[bool, Dict[str, Union[Dict, List]]]]:
            A dictionary representing the success response data, structured as follows:
            {
                "success": <success>,
                "data": {
                    "data": <data> if data is provided,
                    "item": <item> if item is provided,
                    "items": <items> if items are provided
                }
            }
    """
    if data is not None:
        response_data = {"success": success, "data": data}
    elif item is not None:
        response_data = {"success": success, "data": {"item": item}}
    elif items is not None:
        response_data = {"success": success, "data": {"items": items}}
    else:
        response_data = {"success": success, "data": {}}

    return response_data
