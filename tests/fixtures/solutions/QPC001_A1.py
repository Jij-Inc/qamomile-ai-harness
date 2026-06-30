import qamomile.circuit as qmc


@qmc.qkernel
def solve() -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(1, name="q")
    q[0] = qmc.h(q[0])
    return q
