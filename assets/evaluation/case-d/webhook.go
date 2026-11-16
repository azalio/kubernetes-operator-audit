// SYNTHETIC AUDIT FIXTURE: pseudocode, not compilable or deployable Go.
// Two alternative mutating admission implementations; only one would be installed.
// Contract: preserve user containers and ensure exactly one named audit-agent sidecar.
// The API permits Pods that already contain that sidecar. Review both alternatives.
// The admission configuration uses reinvocationPolicy: IfNeeded.
func MutateA(pod Pod) Pod {
    pod.Spec.Containers = append(pod.Spec.Containers, auditSidecar("audit-agent"))
    return pod
}

func MutateB(pod Pod) Pod {
    for _, container := range pod.Spec.Containers {
        if container.Name == "audit-agent" {
            return pod
        }
    }
    pod.Spec.Containers = append(pod.Spec.Containers, auditSidecar("audit-agent"))
    return pod
}
// auditSidecar constructs a valid deterministic container. TLS/deployment are not supplied.
// No claim is made about image policy or how a second webhook changes this object.
