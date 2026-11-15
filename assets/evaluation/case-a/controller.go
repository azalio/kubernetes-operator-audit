// SYNTHETIC AUDIT FIXTURE: incomplete Go excerpt, not a deployable operator.
// Target: multi-tenant CloudDatabase CR, one paid external database per CR.
// provider.Create allocates a NEW billable database on every call, no deduplication.
// provider.Delete can fail transiently; Update below persists metadata.
func (r *Reconciler) Reconcile(ctx context.Context, req Request) error {
    obj, err := r.Get(ctx, req.Namespace, req.Name)
    if IsNotFound(err) { return nil }
    if err != nil { return err }
    if obj.DeletionTimestamp != nil {
        _ = r.provider.Delete(ctx, obj.Status.ExternalID)
        obj.Finalizers = nil
        return r.Update(ctx, obj)
    }
    id, err := r.provider.Create(ctx, obj.Spec.Plan)
    if err != nil { return err }
    obj.Status.ExternalID = id
    obj.Status.Ready = true // provider creation is asynchronous; Ready not yet checked
    return r.UpdateStatus(ctx, obj)
}
