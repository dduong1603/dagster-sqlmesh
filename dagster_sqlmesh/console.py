from ast import Call
from typing import Optional, Dict, Set, Any, Union, Callable, List
from dataclasses import dataclass
import uuid
import unittest

from sqlmesh import SQL
from sqlmesh.core.console import Console
from sqlmesh.core.plan import Plan
from sqlmesh.core.context_diff import ContextDiff
from sqlmesh.core.plan import Plan, PlanBuilder
from sqlmesh.core.table_diff import RowDiff, SchemaDiff
from sqlmesh.core.environment import EnvironmentNamingInfo
from sqlmesh.core.snapshot import (
    Snapshot,
    SnapshotChangeCategory,
    SnapshotId,
    SnapshotInfoLike,
    start_date,
)
from sqlmesh.core.test import ModelTest


@dataclass
class StartMigrationProgress:
    total_tasks: int


@dataclass
class UpdateMigrationProgress:
    num_tasks: int


@dataclass
class StopMigrationProgress:
    pass


@dataclass
class StartPlanEvaluation:
    plan: Plan


@dataclass
class StopPlanEvaluation:
    pass


@dataclass
class StartEvaluationProgress:
    batches: Dict[Snapshot, int]
    environment_naming_info: EnvironmentNamingInfo
    default_catalog: Optional[str]


@dataclass
class StartSnapshotEvaluationProgress:
    snapshot: Snapshot


@dataclass
class UpdateSnapshotEvaluationProgress:
    snapshot: Snapshot
    batch_idx: int
    duration_ms: Optional[int]


@dataclass
class StopEvaluationProgress:
    success: bool = True


@dataclass
class StartCreationProgress:
    total_tasks: int
    environment_naming_info: EnvironmentNamingInfo
    default_catalog: Optional[str]


@dataclass
class UpdateCreationProgress:
    snapshot: SnapshotInfoLike


@dataclass
class StopCreationProgress:
    success: bool = True


@dataclass
class StartCleanup:
    ignore_ttl: bool


@dataclass
class UpdateCleanupProgress:
    object_name: str


@dataclass
class StopCleanup:
    success: bool = True


@dataclass
class StartPromotionProgress:
    total_tasks: int
    environment_naming_info: EnvironmentNamingInfo
    default_catalog: Optional[str]


@dataclass
class UpdatePromotionProgress:
    snapshot: SnapshotInfoLike
    promoted: bool


@dataclass
class StopPromotionProgress:
    success: bool = True


@dataclass
class UpdateSnapshotMigrationProgress:
    num_tasks: int


@dataclass
class LogMigrationStatus:
    success: bool = True


@dataclass
class StartSnapshotMigrationProgress:
    total_tasks: int


@dataclass
class StopSnapshotMigrationProgress:
    success: bool = True


@dataclass
class StartEnvMigrationProgress:
    total_tasks: int


@dataclass
class UpdateEnvMigrationProgress:
    num_tasks: int


@dataclass
class StopEnvMigrationProgress:
    success: bool = True


@dataclass
class ShowModelDifferenceSummary:
    context_diff: ContextDiff
    environment_naming_info: EnvironmentNamingInfo
    default_catalog: Optional[str]
    no_diff: bool = True
    ignored_snapshot_ids: Optional[Set[SnapshotId]] = None


@dataclass
class PlanEvent:
    plan_builder: PlanBuilder
    auto_apply: bool
    default_catalog: Optional[str]
    no_diff: bool = False
    no_prompts: bool = False


@dataclass
class LogTestResults:
    result: unittest.result.TestResult
    output: str
    target_dialect: str


@dataclass
class ShowSQL:
    sql: str


@dataclass
class LogStatusUpdate:
    message: str


@dataclass
class LogError:
    message: str


@dataclass
class LogSuccess:
    message: str


@dataclass
class LoadingStart:
    message: Optional[str] = None
    id: uuid.UUID = uuid.uuid4()


@dataclass
class LoadingStop:
    id: uuid.UUID


@dataclass
class ShowSchemaDiff:
    schema_diff: SchemaDiff


@dataclass
class ShowRowDiff:
    row_diff: RowDiff
    show_sample: bool = True
    skip_grain_check: bool = False


ConsoleEvent = Union[
    StartPlanEvaluation,
    StopPlanEvaluation,
    StartEvaluationProgress,
    StartSnapshotEvaluationProgress,
    UpdateSnapshotEvaluationProgress,
    StopEvaluationProgress,
    StartCreationProgress,
    UpdateCreationProgress,
    StopCreationProgress,
    StartCleanup,
    UpdateCleanupProgress,
    StopCleanup,
    StartPromotionProgress,
    UpdatePromotionProgress,
    StopPromotionProgress,
    UpdateSnapshotMigrationProgress,
    LogMigrationStatus,
    StopSnapshotMigrationProgress,
    StartEnvMigrationProgress,
    UpdateEnvMigrationProgress,
    StopEnvMigrationProgress,
    ShowModelDifferenceSummary,
    PlanEvent,
    LogTestResults,
    ShowSQL,
    LogStatusUpdate,
    LogError,
    LogSuccess,
    LoadingStart,
    LoadingStop,
    ShowSchemaDiff,
    ShowRowDiff,
    StartMigrationProgress,
    UpdateMigrationProgress,
    StopMigrationProgress,
    StartSnapshotMigrationProgress,
]

ConsoleEventHandler = Callable[[ConsoleEvent], None]


class EventConsole(Console):
    def __init__(self):
        self._handlers: List[ConsoleEventHandler] = []

    def start_plan_evaluation(self, plan: Plan) -> None:
        self.publish(StartPlanEvaluation(plan))

    def stop_plan_evaluation(self) -> None:
        self.publish(StopPlanEvaluation())

    def start_evaluation_progress(
        self,
        batches: Dict[Snapshot, int],
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        self.publish(
            StartEvaluationProgress(batches, environment_naming_info, default_catalog)
        )

    def start_snapshot_evaluation_progress(self, snapshot: Snapshot) -> None:
        self.publish(StartSnapshotEvaluationProgress(snapshot))

    def update_snapshot_evaluation_progress(
        self, snapshot: Snapshot, batch_idx: int, duration_ms: Optional[int]
    ) -> None:
        self.publish(UpdateSnapshotEvaluationProgress(snapshot, batch_idx, duration_ms))

    def stop_evaluation_progress(self, success: bool = True) -> None:
        self.publish(StopEvaluationProgress(success))

    def start_creation_progress(
        self,
        total_tasks: int,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        self.publish(
            StartCreationProgress(total_tasks, environment_naming_info, default_catalog)
        )

    def update_creation_progress(self, snapshot: SnapshotInfoLike) -> None:
        self.publish(UpdateCreationProgress(snapshot))

    def stop_creation_progress(self, success: bool = True) -> None:
        self.publish(StopCreationProgress(success))

    def start_cleanup(self, ignore_ttl: bool) -> bool:
        event = StartCleanup(ignore_ttl)
        self.publish(event)
        return True  # Assuming the cleanup should always proceed, or modify as needed

    def update_cleanup_progress(self, object_name: str) -> None:
        self.publish(UpdateCleanupProgress(object_name))

    def stop_cleanup(self, success: bool = True) -> None:
        self.publish(StopCleanup(success))

    def start_promotion_progress(
        self,
        total_tasks: int,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        self.publish(
            StartPromotionProgress(
                total_tasks, environment_naming_info, default_catalog
            )
        )

    def update_promotion_progress(
        self, snapshot: SnapshotInfoLike, promoted: bool
    ) -> None:
        self.publish(UpdatePromotionProgress(snapshot, promoted))

    def stop_promotion_progress(self, success: bool = True) -> None:
        self.publish(StopPromotionProgress(success))

    def start_snapshot_migration_progress(self, total_tasks: int) -> None:
        self.publish(StartSnapshotMigrationProgress(total_tasks))

    def update_snapshot_migration_progress(self, num_tasks: int) -> None:
        self.publish(UpdateSnapshotMigrationProgress(num_tasks))

    def log_migration_status(self, success: bool = True) -> None:
        self.publish(LogMigrationStatus(success))

    def stop_snapshot_migration_progress(self, success: bool = True) -> None:
        self.publish(StopSnapshotMigrationProgress(success))

    def start_env_migration_progress(self, total_tasks: int) -> None:
        self.publish(StartEnvMigrationProgress(total_tasks))

    def update_env_migration_progress(self, num_tasks: int) -> None:
        self.publish(UpdateEnvMigrationProgress(num_tasks))

    def stop_env_migration_progress(self, success: bool = True) -> None:
        self.publish(StopEnvMigrationProgress(success))

    def show_model_difference_summary(
        self,
        context_diff: ContextDiff,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
        no_diff: bool = True,
        ignored_snapshot_ids: Optional[Set[SnapshotId]] = None,
    ) -> None:
        self.publish(
            ShowModelDifferenceSummary(
                context_diff,
                environment_naming_info,
                default_catalog,
                no_diff,
                ignored_snapshot_ids,
            )
        )

    def plan(
        self,
        plan_builder: PlanBuilder,
        auto_apply: bool,
        default_catalog: Optional[str],
        no_diff: bool = False,
        no_prompts: bool = False,
    ) -> None:
        self.publish(
            PlanEvent(plan_builder, auto_apply, default_catalog, no_diff, no_prompts)
        )

    def log_test_results(
        self, result: unittest.result.TestResult, output: str, target_dialect: str
    ) -> None:
        self.publish(LogTestResults(result, output, target_dialect))

    def show_sql(self, sql: str) -> None:
        self.publish(ShowSQL(sql))

    def log_status_update(self, message: str) -> None:
        self.publish(LogStatusUpdate(message))

    def log_error(self, message: str) -> None:
        self.publish(LogError(message))

    def log_success(self, message: str) -> None:
        self.publish(LogSuccess(message))

    def loading_start(self, message: Optional[str] = None) -> uuid.UUID:
        event_id = uuid.uuid4()
        self.publish(LoadingStart(message, event_id))
        return event_id

    def loading_stop(self, id: uuid.UUID) -> None:
        self.publish(LoadingStop(id))

    def show_schema_diff(self, schema_diff: SchemaDiff) -> None:
        self.publish(ShowSchemaDiff(schema_diff))

    def show_row_diff(
        self,
        row_diff: RowDiff,
        show_sample: bool = True,
        skip_grain_check: bool = False,
    ) -> None:
        self.publish(ShowRowDiff(row_diff, show_sample, skip_grain_check))

    def publish(self, event: ConsoleEvent) -> None:
        for handler in self._handlers:
            handler(event)

    def listen(self, handler: ConsoleEventHandler):
        self._handlers.append(handler)


class DebugEventConsole(EventConsole):
    def __init__(self, console: Console):
        super().__init__()
        self._console = console

    def start_plan_evaluation(self, plan: Plan) -> None:
        super().start_plan_evaluation(plan)
        self._console.start_plan_evaluation(plan)

    def stop_plan_evaluation(self) -> None:
        super().stop_plan_evaluation()
        self._console.stop_plan_evaluation()

    def start_evaluation_progress(
        self,
        batches: Dict[Snapshot, int],
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        super().start_evaluation_progress(
            batches, environment_naming_info, default_catalog
        )
        self._console.start_evaluation_progress(
            batches, environment_naming_info, default_catalog
        )

    def start_snapshot_evaluation_progress(self, snapshot: Snapshot) -> None:
        super().start_snapshot_evaluation_progress(snapshot)
        self._console.start_snapshot_evaluation_progress(snapshot)

    def update_snapshot_evaluation_progress(
        self, snapshot: Snapshot, batch_idx: int, duration_ms: Optional[int]
    ) -> None:
        super().update_snapshot_evaluation_progress(snapshot, batch_idx, duration_ms)
        self._console.update_snapshot_evaluation_progress(
            snapshot, batch_idx, duration_ms
        )

    def stop_evaluation_progress(self, success: bool = True) -> None:
        super().stop_evaluation_progress(success)
        self._console.stop_evaluation_progress(success)

    def start_creation_progress(
        self,
        total_tasks: int,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        super().start_creation_progress(
            total_tasks, environment_naming_info, default_catalog
        )
        self._console.start_creation_progress(
            total_tasks, environment_naming_info, default_catalog
        )

    def update_creation_progress(self, snapshot: SnapshotInfoLike) -> None:
        super().update_creation_progress(snapshot)
        self._console.update_creation_progress(snapshot)

    def stop_creation_progress(self, success: bool = True) -> None:
        super().stop_creation_progress(success)
        self._console.stop_creation_progress(success)

    def update_cleanup_progress(self, object_name: str) -> None:
        super().update_cleanup_progress(object_name)
        self._console.update_cleanup_progress(object_name)

    def start_promotion_progress(
        self,
        total_tasks: int,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
    ) -> None:
        super().start_promotion_progress(
            total_tasks, environment_naming_info, default_catalog
        )
        self._console.start_promotion_progress(
            total_tasks, environment_naming_info, default_catalog
        )

    def update_promotion_progress(
        self, snapshot: SnapshotInfoLike, promoted: bool
    ) -> None:
        super().update_promotion_progress(snapshot, promoted)
        self._console.update_promotion_progress(snapshot, promoted)

    def stop_promotion_progress(self, success: bool = True) -> None:
        super().stop_promotion_progress(success)
        self._console.stop_promotion_progress(success)

    def show_model_difference_summary(
        self,
        context_diff: ContextDiff,
        environment_naming_info: EnvironmentNamingInfo,
        default_catalog: Optional[str],
        no_diff: bool = True,
        ignored_snapshot_ids: Optional[Set[SnapshotId]] = None,
    ) -> None:
        super().show_model_difference_summary(
            context_diff,
            environment_naming_info,
            default_catalog,
            no_diff,
            ignored_snapshot_ids,
        )
        self._console.show_model_difference_summary(
            context_diff,
            environment_naming_info,
            default_catalog,
            no_diff,
            ignored_snapshot_ids,
        )

    def plan(
        self,
        plan_builder: PlanBuilder,
        auto_apply: bool,
        default_catalog: Optional[str],
        no_diff: bool = False,
        no_prompts: bool = False,
    ) -> None:
        super().plan(plan_builder, auto_apply, default_catalog, no_diff, no_prompts)
        self._console.plan(
            plan_builder, auto_apply, default_catalog, no_diff, no_prompts
        )

    def log_test_results(
        self, result: unittest.result.TestResult, output: str, target_dialect: str
    ) -> None:
        super().log_test_results(result, output, target_dialect)
        self._console.log_test_results(result, output, target_dialect)

    def show_sql(self, sql: str) -> None:
        super().show_sql(sql)
        self._console.show_sql(sql)

    def log_status_update(self, message: str) -> None:
        super().log_status_update(message)
        self._console.log_status_update(message)

    def log_error(self, message: str) -> None:
        super().log_error(message)
        self._console.log_error(message)

    def log_success(self, message: str) -> None:
        super().log_success(message)
        self._console.log_success(message)

    def loading_start(self, message: Optional[str] = None) -> uuid.UUID:
        event_id = super().loading_start(message)
        self._console.loading_start(message)
        return event_id

    def loading_stop(self, id: uuid.UUID) -> None:
        super().loading_stop(id)
        self._console.loading_stop(id)

    def show_schema_diff(self, schema_diff: SchemaDiff) -> None:
        super().show_schema_diff(schema_diff)
        self._console.show_schema_diff(schema_diff)

    def show_row_diff(
        self,
        row_diff: RowDiff,
        show_sample: bool = True,
        skip_grain_check: bool = False,
    ) -> None:
        super().show_row_diff(row_diff, show_sample)
        self._console.show_row_diff(row_diff, show_sample, skip_grain_check)