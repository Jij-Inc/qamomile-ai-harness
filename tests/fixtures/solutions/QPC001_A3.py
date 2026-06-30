import qamomile.circuit as qmc


@qmc.qkernel
def solve() -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(2, name="q")
    q[0] = qmc.h(q[0])
    q[0], q[1] = qmc.cx(q[0], q[1])
    return q
