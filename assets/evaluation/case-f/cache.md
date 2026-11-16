# SYNTHETIC cached-client design

The Go operator uses controller-runtime v0.20.4 with the default manager client. Only Widget has an explicitly registered watch. The cache options leave ReaderFailOnMissingInformer false; DefaultNamespaces, DefaultLabelSelector and ByObject restrictions are unset. The controller's first authorized Secret reference is read with the cache-backed client.Get(namespace, name); there is no APIReader for that call. Reference authorization and namespace policy are enforced before the read. Required cluster-wide Secret list/watch RBAC exists.

The design document claims: "A named Get retains only the requested Secret; the memory required by Secret reads is independent of the number of unrelated Secrets in the cluster."

The supported scale target includes clusters with 100,000 unrelated Secrets, but no memory/latency benchmark, heap profile, Pod memory limit or runtime result is supplied. Review the claim and identify the smallest verification needed. Do not invent an observed OOM or assume a particular memory-per-object value. Restricting the cache is one possible design change; the API permits authorized references across namespaces, so any such change must preserve that contract.
