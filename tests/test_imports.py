"""Test module imports"""

import pytest


def test_import_main_module():
    """Test that main module imports correctly"""
    from ispy import iSpyTool, Config
    assert iSpyTool is not None
    assert Config is not None


def test_import_device():
    """Test device module import"""
    from ispy.device import DeviceInfo, detect_devices
    assert DeviceInfo is not None
    assert detect_devices is not None


def test_import_health():
    """Test health module import"""
    from ispy.health import HealthScore, HealthCalculator
    assert HealthScore is not None
    assert HealthCalculator is not None


def test_import_modules():
    """Test diagnostic modules import"""
    from ispy.modules import (
        AVAILABLE_MODULES,
        BatteryDiagnostic,
        StorageDiagnostic,
        NetworkDiagnostic,
        SecurityDiagnostic,
    )
    assert len(AVAILABLE_MODULES) == 10
    assert BatteryDiagnostic is not None


def test_config_creation():
    """Test config can be created"""
    from ispy.config import Config
    config = Config()
    assert config is not None
    assert hasattr(config, 'openai_api_key')
    assert hasattr(config, 'enabled_modules')


def test_config_get_method():
    """Test config get method"""
    from ispy.config import Config
    config = Config()
    assert config.get('ai_model') is not None
    assert config.get('nonexistent', 'default') == 'default'


def test_tool_creation():
    """Test iSpyTool can be created"""
    from ispy import iSpyTool
    tool = iSpyTool()
    assert tool is not None
    assert hasattr(tool, 'get_connected_devices')
    assert hasattr(tool, 'run_diagnostic')


def test_available_modules():
    """Test get_available_modules returns all modules"""
    from ispy import iSpyTool
    tool = iSpyTool()
    modules = tool.get_available_modules()
    assert 'battery' in modules
    assert 'storage' in modules
    assert 'network' in modules
    assert 'security' in modules
    assert 'thermal' in modules
    assert len(modules) == 10


def test_health_calculator():
    """Test health calculator"""
    from ispy.health import HealthCalculator
    calc = HealthCalculator()
    result = calc.calculate({
        'battery_level': 80,
        'battery_cycles': 300,
        'storage_usage': 50.0,
    })
    assert 'overall_score' in result
    assert 'overall_grade' in result
    assert result['overall_score'] > 0
