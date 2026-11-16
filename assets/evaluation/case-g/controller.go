// Synthetic pseudocode for static review, not a buildable/deployable operator.
// Dependency: sigs.k8s.io/controller-runtime v0.20.4.
// Contract: create the Deployment for a new Widget; refresh Widget readiness
// from Deployment status; clean up external state when the Widget is deleted.
// Widget has a status subresource. Metadata/status updates do not increment its
// generation. Deployment status updates do not increment its generation either.
// All watches and scheduling are shown. No periodic polling, external enqueue,
// generic events or scheduled controller restart supplies additional work.
// RBAC, ownership, cleanup idempotence and helper error handling are correct.
// Helpers do not schedule work. Normal reconciliation correctly derives Ready
// from Deployment status. Initially the Widget has no finalizer or children.

func (r *WidgetReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    widget := &Widget{}
    if err := r.Get(ctx, req.NamespacedName, widget); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    if !widget.DeletionTimestamp.IsZero() {
        if err := r.cleanupExternal(ctx, widget); err != nil {
            return ctrl.Result{}, err
        }
        controllerutil.RemoveFinalizer(widget, cleanupFinalizer)
        return ctrl.Result{}, r.Update(ctx, widget)
    }
    if !controllerutil.ContainsFinalizer(widget, cleanupFinalizer) {
        controllerutil.AddFinalizer(widget, cleanupFinalizer)
        return ctrl.Result{}, r.Update(ctx, widget)
    }
    if err := r.ensureDeployment(ctx, widget); err != nil {
        return ctrl.Result{}, err
    }
    return ctrl.Result{}, r.refreshReadyFromDeployment(ctx, widget)
}

func (r *WidgetReconciler) SetupWithManager(mgr ctrl.Manager) error {
    return ctrl.NewControllerManagedBy(mgr).
        For(&Widget{}).
        Owns(&appsv1.Deployment{}).
        WithEventFilter(predicate.GenerationChangedPredicate{}).
        Complete(r)
}
