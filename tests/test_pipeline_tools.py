from tools.pipeline_tools import generate_pipeline_yaml, validate_pipeline_yaml


def test_pipeline_yaml_generation():
    yaml_text = generate_pipeline_yaml(
        identifier="my_pipeline",
        name="My Pipeline",
        steps=[],
        requires_approval=True,
    )
    assert "pipeline" in yaml_text
    assert "HarnessApproval" in yaml_text


def test_pipeline_yaml_validation():
    yaml_text = generate_pipeline_yaml(
        identifier="my_pipeline",
        name="My Pipeline",
        steps=[],
    )
    result = validate_pipeline_yaml(yaml_text)
    assert result["valid"]


def test_pipeline_yaml_invalid_name():
    yaml_text = generate_pipeline_yaml(
        identifier="my_pipeline",
        name="123 Invalid Name",
        steps=[],
    )
    result = validate_pipeline_yaml(yaml_text)
    assert not result["valid"]
