// SYNTHETIC AUDIT FIXTURE: complete decision path, helpers summarized, not runnable Go.
// Namespaced Website API contract: spec.expose=true exposes the site through one Ingress;
// spec.expose=false removes that route while retaining the Website and its Service.
// EnsureIngress is idempotent, sets this Website's UID as owner, rejects foreign ownership,
// and operates in the Website namespace. No other controller manages these Ingresses.
func ReconcileWebsite(ctx Context, key Key) error {
    site, err := GetWebsite(ctx, key)
    if IsNotFound(err) { return nil }
    if err != nil { return err }
    if site.DeletionTimestamp != nil { return nil } // Kubernetes GC handles children.
    if err := EnsureService(ctx, site); err != nil { return err }
    if site.Spec.Expose {
        if err := EnsureIngress(ctx, site); err != nil { return err }
    }
    return nil
}
// Spec changes enqueue reconciliation. Service/Ingress owner references are valid.
// There are no external resources, persistent data, custom finalizers or readiness claims.
