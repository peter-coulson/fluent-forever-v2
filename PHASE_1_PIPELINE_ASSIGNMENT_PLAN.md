# Phase 1: Universal Pipeline Assignment System

## Overview
Implement pipeline-specific access control across all provider types (data, audio, image, sync) to enable secure multi-pipeline workflows with proper resource isolation and cost control.

## Scope
This phase focuses on the foundational registry-level architecture that controls which pipelines can access which providers. **No provider-specific enhancements** - just the access control framework.

## Core Enhancement Areas

### 1. Registry-Level Pipeline Filtering
- **Universal Access Control**: All provider types support pipeline-specific assignments
- **Single Filter Method**: `get_providers_for_pipeline(pipeline_name)` returns filtered provider dict
- **Cross-Type Validation**: Ensures consistent pipeline assignments across all provider categories
- **Wildcard Support**: Providers can be assigned to all pipelines using "*" notation

### 2. Configuration Schema Extension
- **Pipeline Assignment Fields**: All provider configs support optional "pipelines" array
- **Backward Compatibility**: Providers without pipeline assignments default to universal access
- **Validation Rules**: Config validation prevents invalid pipeline assignments

### 3. Context Injection Enhancement
- **Filtered Provider Injection**: RunCommand only injects providers authorized for current pipeline
- **Clear Error Messages**: Explicit feedback when unauthorized provider access attempted
- **Multi-Type Support**: Context receives filtered providers for all provider types

## Implementation Areas

### 1. Provider Registry Core
- **Assignment Storage**: Maintain provider-to-pipeline mappings for all provider types
- **Universal Filtering**: Single method filters data, audio, image, and sync providers
- **Validation Logic**: Cross-provider validation during registry initialization

### 2. Configuration Loading
- **Schema Updates**: Support pipeline assignment arrays in provider configuration
- **Default Handling**: Providers without assignments get universal access for backward compatibility
- **Conflict Detection**: Validate pipeline assignments don't create resource conflicts

### 3. CLI Integration
- **Context Creation**: Update RunCommand to use filtered provider injection
- **Error Handling**: Clear messages when pipelines request unauthorized providers
- **Debug Support**: Logging to show which providers are available to each pipeline

## Benefits
- **Universal Security**: Pipeline-based access control across all external services
- **Cost Control**: Foundation for restricting expensive APIs to authorized pipelines
- **Resource Isolation**: Prevents pipeline interference at the registry level
- **Clean Architecture**: Single point of control for all provider access
- **Backward Compatibility**: Existing configs continue working unchanged

## Success Criteria
- ✅ Any provider type can be restricted to specific pipelines via config
- ✅ Existing single-pipeline setups work without modification
- ✅ Clear error messages when unauthorized access attempted
- ✅ Registry provides filtered provider access for any pipeline name
- ✅ Config validation catches invalid pipeline assignments

## Dependencies
- **None** - This is the foundational enhancement that other phases build upon

## Deliverables
- Enhanced `ProviderRegistry` with pipeline filtering
- Updated configuration schema supporting pipeline assignments
- Modified `RunCommand` context injection using filtered providers
- Configuration validation for pipeline assignments
- Updated documentation reflecting new access control model
