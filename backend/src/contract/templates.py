"""
Contract Template Library

Provides standardized contract templates for different transaction scenarios.
Following Black2 Protocol v1.0 Section 2.3 and 2.7.
"""

from typing import Dict, Any, List
import hashlib
import json


# Standard contract templates
CONTRACT_TEMPLATES = {
    "software_sale": {
        "template_id": "TPL_SOFTWARE_001",
        "name": "软件/工具销售合约",
        "version": "1.0",
        "fields": {
            "product_name": {"type": "string", "required": True, "description": "商品名称"},
            "version": {"type": "string", "required": True, "description": "版本号"},
            "system_requirements": {"type": "string", "required": True, "description": "适配系统"},
            "quantifiable_features": {"type": "array", "required": True, "description": "核心功能量化指标"},
            "usage_license": {"type": "string", "required": True, "enum": ["personal", "commercial_single", "commercial_multi"]},
            "duration": {"type": "string", "required": True, "enum": ["permanent", "1year", "6months", "3months"]},
            "auto_confirm_hours": {"type": "integer", "required": True, "default": 72, "min": 24, "max": 168},
            "refund_policy": {"type": "string", "required": True, "enum": ["no_refund", "7days", "not_working"]},
            "delivery_items": {"type": "object", "required": True}
        }
    },
    
    "ai_custom_task": {
        "template_id": "TPL_AI_TASK_001",
        "name": "AI定制化任务合约",
        "version": "1.0",
        "fields": {
            "task_id": {"type": "string", "required": True},
            "task_requirements": {"type": "string", "required": True, "description": "任务需求（量化标准）"},
            "data_delivery": {"type": "string", "required": True, "description": "数据交付要求"},
            "compute_environment": {"type": "object", "required": True, "description": "运算环境配置"},
            "deadline_hours": {"type": "integer", "required": True},
            "acceptance_criteria": {"type": "string", "required": True, "description": "结果验收标准"},
            "auto_confirm_hours": {"type": "integer", "required": True, "default": 48, "min": 24, "max": 72}
        }
    },
    
    "ai_traffic_service": {
        "template_id": "TPL_TRAFFIC_001",
        "name": "AI引流服务合约",
        "version": "1.0",
        "fields": {
            "traffic_channel": {"type": "string", "required": True, "enum": ["wechat", "qq", "app_register"]},
            "fan_type": {"type": "string", "required": True, "enum": ["precise", "general"]},
            "price_per_fan": {"type": "number", "required": True},
            "total_target": {"type": "integer", "required": True},
            "deadline_hours": {"type": "integer", "required": True},
            "acceptance_criteria": {"type": "string", "required": True},
            "prepayment_ratio": {"type": "number", "required": True, "default": 0.4, "min": 0.3, "max": 0.5}
        }
    },
    
    "data_delivery": {
        "template_id": "TPL_DATA_001",
        "name": "数据交付合约",
        "version": "1.0",
        "fields": {
            "data_type": {"type": "string", "required": True},
            "data_format": {"type": "string", "required": True},
            "data_size": {"type": "string", "required": True},
            "quality_standard": {"type": "string", "required": True},
            "delivery_method": {"type": "string", "required": True},
            "auto_confirm_hours": {"type": "integer", "required": True, "default": 72}
        }
    }
}


def get_template(template_id: str) -> Dict[str, Any]:
    """Get a contract template by ID."""
    for tpl in CONTRACT_TEMPLATES.values():
        if tpl["template_id"] == template_id:
            return tpl
    raise ValueError(f"Template not found: {template_id}")


def list_templates() -> List[Dict[str, Any]]:
    """List all available templates."""
    return [
        {
            "template_id": tpl["template_id"],
            "name": tpl["name"],
            "version": tpl["version"]
        }
        for tpl in CONTRACT_TEMPLATES.values()
    ]


def generate_contract_hash(contract_data: Dict[str, Any]) -> str:
    """
    Generate SHA-256 hash for contract data.
    Following Black2 Protocol Section 2.7 Rule 1.
    
    Contract Hash = SHA256(all contract terms + file_hash + seller_id + timestamp)
    """
    # Ensure consistent ordering for deterministic hashing
    normalized = json.dumps(contract_data, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def validate_contract_against_template(template_id: str, contract_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate contract data against template requirements.
    
    Returns:
        {
            "valid": bool,
            "errors": list of error messages
        }
    """
    try:
        template = get_template(template_id)
    except ValueError as e:
        return {"valid": False, "errors": [str(e)]}
    
    errors = []
    
    # Check required fields
    for field_name, field_spec in template["fields"].items():
        if field_spec.get("required", False) and field_name not in contract_data:
            errors.append(f"Missing required field: {field_name}")
        
        # Check enum values
        if field_name in contract_data and "enum" in field_spec:
            if contract_data[field_name] not in field_spec["enum"]:
                errors.append(f"Invalid value for {field_name}: must be one of {field_spec['enum']}")
        
        # Check numeric ranges
        if field_name in contract_data and field_spec["type"] in ["integer", "number"]:
            value = contract_data[field_name]
            if "min" in field_spec and value < field_spec["min"]:
                errors.append(f"{field_name} must be >= {field_spec['min']}")
            if "max" in field_spec and value > field_spec["max"]:
                errors.append(f"{field_name} must be <= {field_spec['max']}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def detect_effect_promise(description: str) -> Dict[str, Any]:
    """
    Detect effect promises in product description.
    Following Black2 Protocol Section 2.7 Rule 5.
    
    Returns:
        {
            "has_effect_promise": bool,
            "detected_keywords": list of detected keywords,
            "warning": warning message if effect promise detected
        }
    """
    effect_keywords = [
        "可提升", "可提高", "可帮助", "可实现", "能保证", "确保",
        "盈利", "赚钱", "收益", "业绩", "转化率提升",
        "一定", "保证", "guaranteed", "promise", "ensure profit",
        "可解决所有问题", "无风险", "稳赚"
    ]
    
    detected = []
    text_lower = description.lower()
    
    for keyword in effect_keywords:
        if keyword.lower() in text_lower:
            detected.append(keyword)
    
    has_promise = len(detected) > 0
    
    return {
        "has_effect_promise": has_promise,
        "detected_keywords": detected,
        "warning": "⚠️ 检测到效果承诺内容。根据协议规则，一旦买家投诉效果未达预期，仲裁将直接判定卖家违约，全额退款并扣除保证金。" if has_promise else None
    }
