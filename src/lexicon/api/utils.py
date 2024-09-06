from uuid import uuid4

from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string


def prep_success_response_data(data=None, item=None, items=None):
    """
    Prepares a success response data dictionary based on the provided parameters.

    Args:
        data: An optional general data object.
        item: An optional specific item object.
        items: An optional list of items.

    Returns:
        dict: A dictionary representing the success response data. The dictionary has the following structure:
            {
                "success": True,
                "data": {
                    <specific data based on the provided parameters>
                }
            }
    """

    response_data = {"success": True}

    if data is not None:
        response_data["data"] = data
    elif item is not None:
        response_data["data"] = {"item": item}
    elif items is not None:
        response_data["data"] = {"items": items}
    else:
        response_data["data"] = {}

    return response_data


def slugify_instance(inst, label, reserved=(), max_length=30, field_name="slug", *args, **kwargs):
    """
    Generate a unique slug for an instance based on a label.

    Args:
        inst: The instance for which the slug is being generated.
        label (str): The label used to generate the base slug.
        reserved (iterable, optional): Reserved slugs that should be excluded.
        max_length (int, optional): The maximum length of the slug. Default is 30.
        field_name (str, optional): The name of the slug field. Default is "slug".
        *args: Additional positional arguments to filter the queryset.
        **kwargs: Additional keyword arguments to filter the queryset.

    Returns:
        None

    """
    base_value = slugify(label)[:max_length]

    if base_value is not None and base_value.strip() in reserved:
        base_value = None

    if not base_value:
        base_value = uuid4().hex[:12]

    base_qs = type(inst).objects.all()

    if inst.id:
        base_qs = base_qs.exclude(id=inst.id)

    if args or kwargs:
        base_qs = base_qs.filter(*args, **kwargs)

    setattr(inst, field_name, base_value)

    # If the base slug is already unique, no further mutation is needed
    if not base_qs.filter(**{"{}__iexact".format(field_name): base_value}).exists():
        return

    # Attempt to generate a shorter unique slug by appending random characters
    sizes = (
        (1, 2),  # (36^2) possibilities, 2 attempts
        (5, 3),  # (36^3) possibilities, 3 attempts
        (20, 5),  # (36^5) possibilities, 20 attempts
        (1, 12),  # (36^12) possibilities, 1 final attempt
    )

    for attempts, size in sizes:
        for _ in range(attempts):
            end = get_random_string(size, allowed_chars="abcdefghijklmnopqrstuvwxyz0123456790")

            value = base_value[: max_length - size - 1] + "-" + end

            setattr(inst, field_name, value)

            if not base_qs.filter(**{"{}__iexact".format(field_name): value}).exists():
                return
