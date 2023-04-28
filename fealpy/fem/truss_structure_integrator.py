import numpy as np


class TrussStructureIntegrator:
    def __init__(self, E, A, q=3):
        self.E = E  # 杨氏模量
        self.A = A  # 单元横截面积
        self.q = q # 积分公式

    def assembly_cell_matrix(self, space, index=np.s_[:], cellmeasure=None,
            out=None):
        """
        @brief 组装单元网格
        """
        assert isinstance(space, tuple) 
        space0 = space[0]
        mesh = space0.mesh
        GD = mesh.geo_dimension()

        assert  len(space) == GD

        if cellmeasure is None:
            cellmeasure = mesh.entity_measure('cell', index=index)

        NC = len(cellmeasure)

        c = self.E*self.A
        tan = mesh.cell_unit_tangent(index=index)
        R = np.einsum('ik, im->ikm', tan, tan)
        R *=c/cellmeasure[:, None, None]

        ldof = 2 # 一个单元两个自由度, @TODO 高次元的情形？本科毕业论文
        if out is None:
            K = np.zeros((NC, GD*ldof, GD*ldof), dtype=np.float64)
        else:
            assert out.shape == (NC, GD*ldof, GD*ldof)
            K = out

        if space0.doforder == 'sdofs':
            for i in range(GD):
                for j in range(i, GD):
                    if i == j:
                        K[:, i::ldof, i::ldof] += R[i, i] 
                    else:
                        K[:, i::ldof, j::ldof] -= R[i, j] 
                        K[:, j::ldof, i::ldof] -= R[j, i] 
        elif space0.doforder == 'vdims':
            for i in range(ldof):
                for j in range(i, ldof):
                    if i == j:
                        K[:, i*GD:(i+1)*GD, i*GD:(i+1)*GD] += R
                    else:
                        K[:, i*GD:(i+1)*GD, j*GD:(j+1)*GD] -= R
                        K[:, j*GD:(j+1)*GD, i*GD:(i+1)*GD] -= R

        if out is None:
            return K