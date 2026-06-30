import qamomile.circuit as qmc


@qmc.qkernel
def solve(n: qmc.UInt) -> qmc.Vector[qmc.Qubit]:
    q = qmc.qubit_array(n, name="q")
    q = qmc.h(q)
    return q
