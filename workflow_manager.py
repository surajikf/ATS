"""
Advanced Workflow Management Module for IKF HR Platform
Multi-stage evaluation workflows, automated scheduling, and collaborative evaluation.
"""

import logging
import uuid
from typing import Dict, List, Tuple, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import streamlit as st
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class StageStatus(Enum):
    """Stage status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"

class EvaluationType(Enum):
    """Evaluation type enumeration."""
    SCREENING = "screening"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    CULTURAL = "cultural"
    REFERENCE = "reference"
    BACKGROUND = "background"
    FINAL = "final"

@dataclass
class WorkflowStage:
    """Represents a stage in the evaluation workflow."""
    stage_id: str
    name: str
    description: str
    evaluation_type: EvaluationType
    required_approvers: List[str]
    optional_approvers: List[str]
    estimated_duration_hours: int
    dependencies: List[str]  # List of stage IDs this stage depends on
    criteria: Dict[str, Any]  # Evaluation criteria for this stage
    status: StageStatus = StageStatus.PENDING
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    assigned_evaluators: List[str] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.assigned_evaluators is None:
            self.assigned_evaluators = []

@dataclass
class WorkflowInstance:
    """Represents an instance of a workflow for a specific candidate."""
    instance_id: str
    workflow_template_id: str
    candidate_id: str
    position: str
    stages: List[WorkflowStage]
    current_stage: int = 0
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_date: datetime = None
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    assigned_hr_manager: str = ""
    priority: str = "medium"  # low, medium, high, urgent
    estimated_completion: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_date is None:
            self.created_date = datetime.now()

@dataclass
class EvaluationResult:
    """Represents the result of an evaluation stage."""
    evaluation_id: str
    stage_id: str
    candidate_id: str
    evaluator_id: str
    evaluation_type: EvaluationType
    score: float  # 0-100
    feedback: str
    recommendation: str  # pass, fail, conditional, needs_improvement
    criteria_ratings: Dict[str, float]  # Individual criteria scores
    attachments: List[str] = None  # File paths or URLs
    evaluation_date: datetime = None
    next_steps: str = ""
    
    def __post_init__(self):
        if self.evaluation_date is None:
            self.evaluation_date = datetime.now()
        if self.attachments is None:
            self.attachments = []

class WorkflowManager:
    """
    Advanced workflow management system for HR evaluation processes.
    Handles multi-stage workflows, automated scheduling, and collaborative evaluation.
    """
    
    def __init__(self):
        """Initialize the workflow manager."""
        self.workflow_templates = {}
        self.active_workflows = {}
        self.evaluation_results = {}
        self.user_permissions = {}
        self.notification_settings = {}
        
        # Workflow templates cache
        self.template_cache = {}
        self.cache_timestamp = None
        
        # Automated scheduling
        self.scheduler_active = False
        self.scheduler_thread = None
        
        logger.info("Workflow Manager initialized successfully")
    
    def create_workflow_template(self, template_data: Dict[str, Any]) -> str:
        """
        Create a new workflow template.
        
        Args:
            template_data (Dict[str, Any]): Template configuration
            
        Returns:
            str: Template ID
        """
        try:
            template_id = str(uuid.uuid4())
            
            # Validate template data
            required_fields = ['name', 'description', 'stages', 'estimated_duration_days']
            for field in required_fields:
                if field not in template_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create stages
            stages = []
            for stage_data in template_data['stages']:
                stage = WorkflowStage(
                    stage_id=str(uuid.uuid4()),
                    name=stage_data['name'],
                    description=stage_data['description'],
                    evaluation_type=EvaluationType(stage_data['evaluation_type']),
                    required_approvers=stage_data.get('required_approvers', []),
                    optional_approvers=stage_data.get('optional_approvers', []),
                    estimated_duration_hours=stage_data.get('estimated_duration_hours', 24),
                    dependencies=stage_data.get('dependencies', []),
                    criteria=stage_data.get('criteria', {})
                )
                stages.append(stage)
            
            # Create template
            template = {
                'template_id': template_id,
                'name': template_data['name'],
                'description': template_data['description'],
                'stages': stages,
                'estimated_duration_days': template_data['estimated_duration_days'],
                'created_date': datetime.now(),
                'created_by': template_data.get('created_by', 'system'),
                'is_active': template_data.get('is_active', True),
                'version': template_data.get('version', '1.0'),
                'tags': template_data.get('tags', [])
            }
            
            self.workflow_templates[template_id] = template
            
            # Clear cache
            self._clear_template_cache()
            
            logger.info(f"Created workflow template: {template_data['name']} (ID: {template_id})")
            return template_id
            
        except Exception as e:
            logger.error(f"Error creating workflow template: {str(e)}")
            raise
    
    def instantiate_workflow(self, template_id: str, candidate_data: Dict[str, Any]) -> str:
        """
        Create a new workflow instance from a template.
        
        Args:
            template_id (str): Template ID to use
            candidate_data (Dict[str, Any]): Candidate information
            
        Returns:
            str: Workflow instance ID
        """
        try:
            if template_id not in self.workflow_templates:
                raise ValueError(f"Template not found: {template_id}")
            
            template = self.workflow_templates[template_id]
            
            # Create workflow instance
            instance_id = str(uuid.uuid4())
            
            # Clone stages for this instance
            stages = []
            for stage in template['stages']:
                instance_stage = WorkflowStage(
                    stage_id=str(uuid.uuid4()),
                    name=stage.name,
                    description=stage.description,
                    evaluation_type=stage.evaluation_type,
                    required_approvers=stage.required_approvers.copy(),
                    optional_approvers=stage.optional_approvers.copy(),
                    estimated_duration_hours=stage.estimated_duration_hours,
                    dependencies=stage.dependencies.copy(),
                    criteria=stage.criteria.copy()
                )
                stages.append(instance_stage)
            
            # Calculate estimated completion
            total_hours = sum(stage.estimated_duration_hours for stage in stages)
            estimated_completion = datetime.now() + timedelta(hours=total_hours)
            
            workflow_instance = WorkflowInstance(
                instance_id=instance_id,
                workflow_template_id=template_id,
                candidate_id=candidate_data['candidate_id'],
                position=candidate_data['position'],
                stages=stages,
                assigned_hr_manager=candidate_data.get('assigned_hr_manager', ''),
                priority=candidate_data.get('priority', 'medium'),
                estimated_completion=estimated_completion
            )
            
            self.active_workflows[instance_id] = workflow_instance
            
            # Send notifications
            self._send_workflow_start_notifications(workflow_instance)
            
            logger.info(f"Instantiated workflow for candidate: {candidate_data['candidate_id']}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Error instantiating workflow: {str(e)}")
            raise
    
    def start_workflow(self, instance_id: str) -> bool:
        """
        Start a workflow instance.
        
        Args:
            instance_id (str): Workflow instance ID
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            if workflow.status != WorkflowStatus.DRAFT:
                raise ValueError(f"Cannot start workflow in status: {workflow.status}")
            
            # Update status
            workflow.status = WorkflowStatus.ACTIVE
            workflow.start_date = datetime.now()
            
            # Start first stage
            if workflow.stages:
                workflow.stages[0].status = StageStatus.IN_PROGRESS
                workflow.stages[0].start_date = datetime.now()
                
                # Assign evaluators
                self._assign_evaluators_to_stage(workflow.stages[0])
            
            # Send notifications
            self._send_stage_start_notifications(workflow, 0)
            
            logger.info(f"Started workflow: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting workflow: {str(e)}")
            return False
    
    def complete_stage(self, instance_id: str, stage_id: str, evaluation_result: EvaluationResult) -> bool:
        """
        Complete a workflow stage with evaluation results.
        
        Args:
            instance_id (str): Workflow instance ID
            stage_id (str): Stage ID to complete
            evaluation_result (EvaluationResult): Evaluation results
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            # Find the stage
            stage = None
            stage_index = -1
            for i, s in enumerate(workflow.stages):
                if s.stage_id == stage_id:
                    stage = s
                    stage_index = i
                    break
            
            if not stage:
                raise ValueError(f"Stage not found: {stage_id}")
            
            if stage.status != StageStatus.IN_PROGRESS:
                raise ValueError(f"Stage is not in progress: {stage.status}")
            
            # Store evaluation result
            self.evaluation_results[evaluation_result.evaluation_id] = evaluation_result
            
            # Check if all required evaluators have completed
            if self._is_stage_complete(workflow, stage):
                # Complete the stage
                stage.status = StageStatus.COMPLETED
                stage.completion_date = datetime.now()
                
                # Check if candidate passed this stage
                if self._evaluate_stage_result(workflow, stage):
                    # Move to next stage
                    if stage_index + 1 < len(workflow.stages):
                        next_stage = workflow.stages[stage_index + 1]
                        if self._can_start_stage(workflow, next_stage):
                            next_stage.status = StageStatus.IN_PROGRESS
                            next_stage.start_date = datetime.now()
                            self._assign_evaluators_to_stage(next_stage)
                            
                            # Send notifications
                            self._send_stage_start_notifications(workflow, stage_index + 1)
                        else:
                            next_stage.status = StageStatus.BLOCKED
                    else:
                        # All stages completed
                        workflow.status = WorkflowStatus.COMPLETED
                        workflow.completion_date = datetime.now()
                        
                        # Send completion notifications
                        self._send_workflow_completion_notifications(workflow)
                else:
                    # Candidate failed this stage
                    workflow.status = WorkflowStatus.CANCELLED
                    
                    # Send failure notifications
                    self._send_workflow_failure_notifications(workflow, stage)
            
            logger.info(f"Completed stage: {stage_id} in workflow: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing stage: {str(e)}")
            return False
    
    def get_workflow_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Get current status of a workflow instance.
        
        Args:
            instance_id (str): Workflow instance ID
            
        Returns:
            Dict[str, Any]: Workflow status information
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            # Calculate progress
            completed_stages = sum(1 for stage in workflow.stages if stage.status == StageStatus.COMPLETED)
            total_stages = len(workflow.stages)
            progress_percentage = (completed_stages / total_stages * 100) if total_stages > 0 else 0
            
            # Calculate time metrics
            current_time = datetime.now()
            elapsed_time = current_time - workflow.start_date if workflow.start_date else timedelta(0)
            remaining_time = workflow.estimated_completion - current_time if workflow.estimated_completion else timedelta(0)
            
            status_info = {
                'instance_id': instance_id,
                'candidate_id': workflow.candidate_id,
                'position': workflow.position,
                'status': workflow.status.value,
                'current_stage': workflow.current_stage,
                'progress_percentage': progress_percentage,
                'completed_stages': completed_stages,
                'total_stages': total_stages,
                'elapsed_time_hours': elapsed_time.total_seconds() / 3600,
                'remaining_time_hours': remaining_time.total_seconds() / 3600 if remaining_time > timedelta(0) else 0,
                'stages': [
                    {
                        'stage_id': stage.stage_id,
                        'name': stage.name,
                        'status': stage.status.value,
                        'evaluation_type': stage.evaluation_type.value,
                        'start_date': stage.start_date.isoformat() if stage.start_date else None,
                        'completion_date': stage.completion_date.isoformat() if stage.completion_date else None,
                        'assigned_evaluators': stage.assigned_evaluators
                    }
                    for stage in workflow.stages
                ],
                'assigned_hr_manager': workflow.assigned_hr_manager,
                'priority': workflow.priority,
                'created_date': workflow.created_date.isoformat(),
                'start_date': workflow.start_date.isoformat() if workflow.start_date else None,
                'estimated_completion': workflow.estimated_completion.isoformat() if workflow.estimated_completion else None
            }
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {'error': str(e)}
    
    def get_user_workflows(self, user_id: str, include_completed: bool = False) -> List[Dict[str, Any]]:
        """
        Get workflows assigned to a specific user.
        
        Args:
            user_id (str): User ID
            include_completed (bool): Include completed workflows
            
        Returns:
            List[Dict[str, Any]]: List of workflow statuses
        """
        try:
            user_workflows = []
            
            for instance_id, workflow in self.active_workflows.items():
                # Check if user is involved in this workflow
                is_involved = False
                
                # Check if user is HR manager
                if workflow.assigned_hr_manager == user_id:
                    is_involved = True
                
                # Check if user is assigned to any stage
                for stage in workflow.stages:
                    if user_id in stage.assigned_evaluators:
                        is_involved = True
                        break
                
                if is_involved:
                    if include_completed or workflow.status != WorkflowStatus.COMPLETED:
                        status_info = self.get_workflow_status(instance_id)
                        user_workflows.append(status_info)
            
            return user_workflows
            
        except Exception as e:
            logger.error(f"Error getting user workflows: {str(e)}")
            return []
    
    def update_workflow_priority(self, instance_id: str, new_priority: str) -> bool:
        """
        Update workflow priority.
        
        Args:
            instance_id (str): Workflow instance ID
            new_priority (str): New priority level
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            valid_priorities = ['low', 'medium', 'high', 'urgent']
            if new_priority not in valid_priorities:
                raise ValueError(f"Invalid priority: {new_priority}")
            
            workflow = self.active_workflows[instance_id]
            old_priority = workflow.priority
            workflow.priority = new_priority
            
            # Recalculate estimated completion based on priority
            self._recalculate_completion_time(workflow)
            
            # Send priority change notifications
            self._send_priority_change_notifications(workflow, old_priority, new_priority)
            
            logger.info(f"Updated workflow priority: {instance_id} from {old_priority} to {new_priority}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating workflow priority: {str(e)}")
            return False
    
    def pause_workflow(self, instance_id: str, reason: str = "") -> bool:
        """
        Pause a workflow instance.
        
        Args:
            instance_id (str): Workflow instance ID
            reason (str): Reason for pausing
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            if workflow.status not in [WorkflowStatus.ACTIVE, WorkflowStatus.DRAFT]:
                raise ValueError(f"Cannot pause workflow in status: {workflow.status}")
            
            workflow.status = WorkflowStatus.PAUSED
            
            # Pause current stage if any
            for stage in workflow.stages:
                if stage.status == StageStatus.IN_PROGRESS:
                    stage.status = StageStatus.BLOCKED
                    stage.notes = f"Workflow paused: {reason}"
                    break
            
            # Send pause notifications
            self._send_workflow_pause_notifications(workflow, reason)
            
            logger.info(f"Paused workflow: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error pausing workflow: {str(e)}")
            return False
    
    def resume_workflow(self, instance_id: str) -> bool:
        """
        Resume a paused workflow instance.
        
        Args:
            instance_id (str): Workflow instance ID
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            if workflow.status != WorkflowStatus.PAUSED:
                raise ValueError(f"Cannot resume workflow in status: {workflow.status}")
            
            workflow.status = WorkflowStatus.ACTIVE
            
            # Resume current stage
            for stage in workflow.stages:
                if stage.status == StageStatus.BLOCKED and "Workflow paused" in stage.notes:
                    stage.status = StageStatus.IN_PROGRESS
                    stage.notes = ""
                    break
            
            # Send resume notifications
            self._send_workflow_resume_notifications(workflow)
            
            logger.info(f"Resumed workflow: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resuming workflow: {str(e)}")
            return False
    
    def add_workflow_comment(self, instance_id: str, user_id: str, comment: str, 
                           stage_id: Optional[str] = None) -> bool:
        """
        Add a comment to a workflow or specific stage.
        
        Args:
            instance_id (str): Workflow instance ID
            user_id (str): User ID adding the comment
            comment (str): Comment text
            stage_id (Optional[str]): Specific stage ID for the comment
            
        Returns:
            bool: Success status
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            
            comment_data = {
                'comment_id': str(uuid.uuid4()),
                'user_id': user_id,
                'comment': comment,
                'timestamp': datetime.now().isoformat(),
                'stage_id': stage_id
            }
            
            # Add comment to workflow or stage
            if stage_id:
                for stage in workflow.stages:
                    if stage.stage_id == stage_id:
                        if not hasattr(stage, 'comments'):
                            stage.comments = []
                        stage.comments.append(comment_data)
                        break
            else:
                if not hasattr(workflow, 'comments'):
                    workflow.comments = []
                workflow.comments.append(comment_data)
            
            # Send comment notifications
            self._send_comment_notifications(workflow, comment_data)
            
            logger.info(f"Added comment to workflow: {instance_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding workflow comment: {str(e)}")
            return False
    
    def _assign_evaluators_to_stage(self, stage: WorkflowStage):
        """Assign evaluators to a stage."""
        # This would implement logic to assign evaluators based on:
        # - Availability
        # - Expertise
        # - Workload
        # - Preferences
        
        # For now, use the required approvers
        stage.assigned_evaluators = stage.required_approvers.copy()
    
    def _is_stage_complete(self, workflow: WorkflowInstance, stage: WorkflowStage) -> bool:
        """Check if a stage is complete based on evaluation results."""
        # Count completed evaluations for this stage
        completed_evaluations = 0
        required_evaluations = len(stage.required_approvers)
        
        for result in self.evaluation_results.values():
            if result.stage_id == stage.stage_id:
                completed_evaluations += 1
        
        return completed_evaluations >= required_evaluations
    
    def _evaluate_stage_result(self, workflow: WorkflowInstance, stage: WorkflowStage) -> bool:
        """Evaluate if a candidate passed a stage."""
        stage_results = []
        
        for result in self.evaluation_results.values():
            if result.stage_id == stage.stage_id:
                stage_results.append(result)
        
        if not stage_results:
            return False
        
        # Calculate average score
        avg_score = sum(result.score for result in stage_results) / len(stage_results)
        
        # Check if all required evaluators recommend pass
        all_passed = all(result.recommendation in ['pass', 'conditional'] for result in stage_results)
        
        # Stage passes if average score >= 70 and all evaluators recommend pass
        return avg_score >= 70 and all_passed
    
    def _can_start_stage(self, workflow: WorkflowInstance, stage: WorkflowStage) -> bool:
        """Check if a stage can be started based on dependencies."""
        if not stage.dependencies:
            return True
        
        # Check if all dependent stages are completed
        for dep_stage_id in stage.dependencies:
            dep_stage = None
            for s in workflow.stages:
                if s.stage_id == dep_stage_id:
                    dep_stage = s
                    break
            
            if not dep_stage or dep_stage.status != StageStatus.COMPLETED:
                return False
        
        return True
    
    def _recalculate_completion_time(self, workflow: WorkflowInstance):
        """Recalculate estimated completion time based on priority."""
        base_hours = sum(stage.estimated_duration_hours for stage in workflow.stages)
        
        # Priority multipliers
        priority_multipliers = {
            'low': 1.5,      # 50% longer
            'medium': 1.0,   # Standard time
            'high': 0.8,     # 20% faster
            'urgent': 0.6    # 40% faster
        }
        
        multiplier = priority_multipliers.get(workflow.priority, 1.0)
        adjusted_hours = base_hours * multiplier
        
        if workflow.start_date:
            workflow.estimated_completion = workflow.start_date + timedelta(hours=adjusted_hours)
    
    def _clear_template_cache(self):
        """Clear workflow template cache."""
        self.template_cache.clear()
        self.cache_timestamp = None
    
    # Notification methods (placeholder implementations)
    def _send_workflow_start_notifications(self, workflow: WorkflowInstance):
        """Send notifications when workflow starts."""
        logger.info(f"Sending workflow start notifications for: {workflow.instance_id}")
    
    def _send_stage_start_notifications(self, workflow: WorkflowInstance, stage_index: int):
        """Send notifications when a stage starts."""
        logger.info(f"Sending stage start notifications for stage {stage_index} in workflow: {workflow.instance_id}")
    
    def _send_workflow_completion_notifications(self, workflow: WorkflowInstance):
        """Send notifications when workflow completes."""
        logger.info(f"Sending workflow completion notifications for: {workflow.instance_id}")
    
    def _send_workflow_failure_notifications(self, workflow: WorkflowInstance, failed_stage: WorkflowStage):
        """Send notifications when workflow fails."""
        logger.info(f"Sending workflow failure notifications for: {workflow.instance_id}")
    
    def _send_priority_change_notifications(self, workflow: WorkflowInstance, old_priority: str, new_priority: str):
        """Send notifications when workflow priority changes."""
        logger.info(f"Sending priority change notifications for workflow: {workflow.instance_id}")
    
    def _send_workflow_pause_notifications(self, workflow: WorkflowInstance, reason: str):
        """Send notifications when workflow is paused."""
        logger.info(f"Sending workflow pause notifications for: {workflow.instance_id}")
    
    def _send_workflow_resume_notifications(self, workflow: WorkflowInstance):
        """Send notifications when workflow resumes."""
        logger.info(f"Sending workflow resume notifications for: {workflow.instance_id}")
    
    def _send_comment_notifications(self, workflow: WorkflowInstance, comment_data: Dict[str, Any]):
        """Send notifications when comments are added."""
        logger.info(f"Sending comment notifications for workflow: {workflow.instance_id}")
    
    def export_workflow_data(self, instance_id: str, format: str = 'json') -> str:
        """
        Export workflow data in specified format.
        
        Args:
            instance_id (str): Workflow instance ID
            format (str): Export format ('json', 'csv')
            
        Returns:
            str: File path to exported data
        """
        try:
            if instance_id not in self.active_workflows:
                raise ValueError(f"Workflow instance not found: {instance_id}")
            
            workflow = self.active_workflows[instance_id]
            status_info = self.get_workflow_status(instance_id)
            
            if format.lower() == 'json':
                return self._export_json_workflow(status_info)
            elif format.lower() == 'csv':
                return self._export_csv_workflow(status_info)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting workflow data: {str(e)}")
            return ""
    
    def _export_json_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Export workflow data as JSON file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_{workflow_data['candidate_id']}_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(workflow_data, f, indent=2, default=str)
            
            logger.info(f"Workflow JSON exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting workflow JSON: {str(e)}")
            return ""
    
    def _export_csv_workflow(self, workflow_data: Dict[str, Any]) -> str:
        """Export workflow data as CSV file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"workflow_{workflow_data['candidate_id']}_{timestamp}.csv"
            
            # Flatten workflow data for CSV
            csv_data = []
            
            # Main workflow info
            csv_data.append({
                'type': 'workflow_info',
                'field': 'candidate_id',
                'value': workflow_data['candidate_id']
            })
            csv_data.append({
                'type': 'workflow_info',
                'field': 'position',
                'value': workflow_data['position']
            })
            csv_data.append({
                'type': 'workflow_info',
                'field': 'status',
                'value': workflow_data['status']
            })
            
            # Stage information
            for stage in workflow_data['stages']:
                csv_data.append({
                    'type': 'stage',
                    'stage_name': stage['name'],
                    'field': 'status',
                    'value': stage['status']
                })
                csv_data.append({
                    'type': 'stage',
                    'stage_name': stage['name'],
                    'field': 'evaluation_type',
                    'value': stage['evaluation_type']
                })
            
            # Create DataFrame and export
            import pandas as pd
            df = pd.DataFrame(csv_data)
            df.to_csv(filename, index=False)
            
            logger.info(f"Workflow CSV exported to: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting workflow CSV: {str(e)}")
            return ""
