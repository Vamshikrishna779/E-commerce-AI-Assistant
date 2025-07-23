def generate_chart_data(result: list) -> tuple:
    """
    Given a list of dictionaries (query result), return chart data and type.
    Example:
        result = [{'category': 'Shoes', 'sales': 100}, {'category': 'Hats', 'sales': 50}]
        → returns ({labels: [...], values: [...], label: ...}, 'bar')
    """
    if not result or not isinstance(result, list) or not isinstance(result[0], dict):
        return None, None

    keys = list(result[0].keys())
    if len(keys) != 2:
        return None, None  # We only visualize 2-column outputs

    x_vals = [row[keys[0]] for row in result]
    y_vals = [row[keys[1]] for row in result]

    # Chart only if Y values are numeric
    if not all(isinstance(y, (int, float)) for y in y_vals):
        return None, None

    chart_data = {
        "labels": x_vals,
        "values": y_vals,
        "label": keys[1]
    }

    chart_type = "bar"
    if len(set(x_vals)) <= 5:
        chart_type = "pie"

    return chart_data, chart_type
