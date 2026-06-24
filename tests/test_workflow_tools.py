from tools.workflow_tools import generate_workflow_yaml, validate_workflow_yaml


def test_workflow_yaml_generation():
    yaml_text = generate_workflow_yaml(
        identifier="my_workflow",
        name="My Workflow",
        parameters=[{"title": "Page 1", "properties": {"sysid": {"type": "string"}}}],
        pipeline_identifier="my_pipeline",
    )
    assert "apiVersion: harness.io/v1" in yaml_text
    assert "kind: Workflow" in yaml_text


def test_workflow_yaml_validation():
    yaml_text = generate_workflow_yaml(
        identifier="my_workflow",
        name="My Workflow",
        parameters=[{"title": "Page 1", "properties": {"sysid": {"type": "string"}}}],
        pipeline_identifier="my_pipeline",
    )
    result = validate_workflow_yaml(yaml_text)
    assert result["valid"]
    assert not result["errors"]


def test_workflow_yaml_invalid():
    result = validate_workflow_yaml("invalid: yaml: [[")
    assert not result["valid"]
