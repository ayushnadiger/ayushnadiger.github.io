"""Verification suite for the final manuscript.

Analytic proofs are in the manuscript. This script independently checks:
  1. the full covariance-normal Gram identity on canonical and randomly rotated exact erasure codes;
  2. trace/determinant formulas for the covariance operator;
  3. the Haar mean-square leakage identity by Monte Carlo with a reported standard error;
  4. exact Knill--Laflamme conditions and stacked-Jacobian rigidity for [[4,2,2]];
  5. exact Knill--Laflamme conditions and stacked-Jacobian rigidity for [[5,1,3]];
  6. numerical Knill--Laflamme conditions and Steane [[7,1,3]] first-order deformation dimensions.
"""
import itertools
import numpy as np
import sympy as sp


def hermitian_basis(n, traceless=False):
    basis=[]
    if not traceless:
        basis.append(np.eye(n,dtype=complex)/np.sqrt(n))
    for k in range(1,n):
        v=np.zeros(n); v[:k]=1; v[k]=-k; v/=np.sqrt(k*(k+1))
        basis.append(np.diag(v).astype(complex))
    for i in range(n):
        for j in range(i+1,n):
            x=np.zeros((n,n),complex); y=np.zeros((n,n),complex)
            x[i,j]=x[j,i]=1/np.sqrt(2)
            y[i,j]=-1j/np.sqrt(2); y[j,i]=1j/np.sqrt(2)
            basis += [x,y]
    return basis


def canonical_encoding(a,b,k,lambdas):
    v=np.zeros((a*b,k),complex)
    for i,lam in enumerate(lambdas):
        if lam<=0: continue
        for ell in range(k): v[i*b+i*k+ell,ell]=np.sqrt(lam)
    return v


def orthogonal_complement(v):
    q,_=np.linalg.qr(v,mode='complete'); return q[:,v.shape[1]:]


def covariance_matrix(sigma,basis):
    C=np.zeros((len(basis),len(basis)))
    for i,A in enumerate(basis):
        a=np.trace(sigma@A).real
        for j,B in enumerate(basis):
            b=np.trace(sigma@B).real
            C[i,j]=np.trace(sigma@(A@B+B@A)/2).real-a*b
    return C


def section_jacobian(v,a,b,k):
    w=orthogonal_complement(v); BA=hermitian_basis(a,True); BL=hermitian_basis(k,True)
    cols=[]
    for p in range(a*b-k):
        for ell in range(k):
            E=np.zeros((a*b-k,k),complex); E[p,ell]=1
            for phase in (1,1j):
                x=w@(phase*E); out=[]
                for T in BA:
                    M=np.kron(T,np.eye(b)); z=x.conj().T@M@v+v.conj().T@M@x
                    z-=np.trace(z)*np.eye(k)/k
                    out.extend(np.trace(L@z).real for L in BL)
                cols.append(out)
    return np.asarray(cols).T, BA


def verify_covariance_theorems():
    print('1. Covariance normal form and explicit invariants')
    rng=np.random.default_rng(20260816)
    cases=[(2,4,2,[.3,.7]),(2,6,3,[.2,.8]),(3,6,2,[.2,.3,.5]),(3,9,3,[.1,.35,.55])]
    for a,b,k,lam in cases:
        # Canonical coordinates.
        v=canonical_encoding(a,b,k,lam); J,BA=section_jacobian(v,a,b,k)
        C=covariance_matrix(np.diag(lam),BA)
        gram_err=np.max(np.abs(J@J.T-4*np.kron(C,np.eye(k*k-1))))
        svals=np.linalg.svd(J,compute_uv=False); svals=svals[svals>1e-10]
        pred=np.repeat(np.sqrt(4*np.linalg.eigvalsh(C)),k*k-1); pred=pred[pred>1e-10]
        spectral_err=np.max(np.abs(np.sort(svals)-np.sort(pred)))

        # Random physical basis on A and independent random logical frame.
        UA=random_unitary(a,rng); UL=random_unitary(k,rng)
        vrot=np.kron(UA,np.eye(b))@v@UL
        sigrot=UA@np.diag(lam)@UA.conj().T
        Jrot,BArot=section_jacobian(vrot,a,b,k)
        Crot=covariance_matrix(sigrot,BArot)
        random_gram_err=np.max(np.abs(Jrot@Jrot.T-4*np.kron(Crot,np.eye(k*k-1))))

        det_formula=a*np.prod(lam)
        for i in range(a):
            for j in range(i+1,a): det_formula*=((lam[i]+lam[j])/2)**2
        trace_formula=a-np.sum(np.asarray(lam)**2)
        det_err=abs(np.linalg.det(C)-det_formula); trace_err=abs(np.trace(C)-trace_formula)
        print(
            f'  (a,b,K)=({a},{b},{k}) '
            f'canonical Gram err={gram_err:.2e}, random-basis Gram err={random_gram_err:.2e}, '
            f'spectral err={spectral_err:.2e}, det err={det_err:.2e}, trace err={trace_err:.2e}'
        )
        assert gram_err<1e-10
        assert random_gram_err<1e-10
        assert spectral_err<1e-10
        assert det_err<1e-10 and trace_err<1e-10


def random_isometry(n,k,rng):
    z=rng.normal(size=(n,k))+1j*rng.normal(size=(n,k)); q,_=np.linalg.qr(z); return q[:,:k]


def random_unitary(n,rng):
    z=rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))
    q,r=np.linalg.qr(z)
    phases=np.diag(r)
    phases=np.where(np.abs(phases)>0, phases/np.abs(phases), 1.0)
    return q@np.diag(np.conj(phases))


def ptrace_a(vec,a,b):
    m=vec.reshape(a,b); return m@m.conj().T


def section_norm_sq(v,a,b,k):
    out=0.
    for T in hermitian_basis(a,True):
        M=np.kron(T,np.eye(b)); z=v.conj().T@M@v; z-=np.trace(z)*np.eye(k)/k
        out+=np.trace(z@z).real
    return out


def verify_leakage(samples=20000):
    print('\n2. Haar leakage identity')
    rng=np.random.default_rng(17)
    for a,b,k in [(2,5,2),(3,5,2),(2,7,3)]:
        v=random_isometry(a*b,k,rng); sigma=sum(ptrace_a(v[:,j],a,b) for j in range(k))/k
        target=section_norm_sq(v,a,b,k)/(k*(k+1)); vals=[]
        for _ in range(samples):
            psi=rng.normal(size=k)+1j*rng.normal(size=k); psi/=np.linalg.norm(psi)
            vals.append(np.linalg.norm(ptrace_a(v@psi,a,b)-sigma,'fro')**2)
        vals=np.asarray(vals,float)
        mc=float(np.mean(vals)); se=float(np.std(vals,ddof=1)/np.sqrt(samples)); err=abs(mc-target)
        z=err/se if se>0 else 0.0
        print(f'  ({a},{b},{k}) MC={mc:.6g}, exact={target:.6g}, error={err:.2e}, SE={se:.2e}, z={z:.2f}')
        # Six standard errors is a conservative, statistically motivated Monte Carlo tolerance.
        assert err <= 6.0*se + 1e-12

def assert_scalar_compressions_exact(V,ops,label):
    K=V.shape[1]
    IK=sp.eye(K)
    for idx,M in enumerate(ops):
        Z=sp.simplify(V.H*M*V)
        alpha=sp.simplify(sp.trace(Z)/K)
        assert sp.simplify(Z-alpha*IK)==sp.zeros(K), f"{label}: KL failure at observable {idx}"
    print(f'  {label}: exactly verified {len(ops)} scalar compressions')


def assert_scalar_compressions_numeric(V,ops,label,tol=1e-10):
    K=V.shape[1]
    IK=np.eye(K,dtype=complex)
    worst=0.0
    for idx,M in enumerate(ops):
        Z=V.conj().T@M@V
        alpha=np.trace(Z)/K
        resid=np.linalg.norm(Z-alpha*IK,'fro')
        worst=max(worst,resid)
        assert resid<tol, f"{label}: KL failure at observable {idx}: {resid}"
    print(f'  {label} KL max residual={worst:.2e}')


# ---------- exact stabilizer examples ----------
I=sp.I; I2=sp.eye(2); X2=sp.Matrix([[0,1],[1,0]]); Y2=sp.Matrix([[0,-I],[I,0]]); Z2=sp.Matrix([[1,0],[0,-1]])
PM={'I':I2,'X':X2,'Y':Y2,'Z':Z2}

def skron(mats):
    out=sp.Matrix([[1]])
    for M in mats: out=sp.kronecker_product(out,M)
    return out

def spauli(s): return skron([PM[c] for c in s])

def bits_to_int(bits):
    x=0
    for b in bits: x=2*x+b
    return x


def exact_422():
    rt2=sp.sqrt(2)
    def e(i):
        v=sp.zeros(16,1); v[i]=1; return v
    pairs=[]; seen=set()
    for bits in itertools.product([0,1],repeat=4):
        i=bits_to_int(bits)
        if i in seen: continue
        comp=tuple(1-q for q in bits); j=bits_to_int(comp); seen|={i,j}; pairs.append((bits,comp))
    code=[]; comp=[]
    for bits,c in pairs:
        i,j=bits_to_int(bits),bits_to_int(c); plus=(e(i)+e(j))/rt2; minus=(e(i)-e(j))/rt2
        if sum(bits)%2==0: code.append(plus); comp.append(minus)
        else: comp.extend([plus,minus])
    V=sp.Matrix.hstack(*code); W=sp.Matrix.hstack(*comp)
    ops=[]
    for q in range(4):
        for p in (X2,Y2,Z2):
            mats=[I2]*4; mats[q]=p; ops.append(skron(mats))
    assert_scalar_compressions_exact(V,ops,'[[4,2,2]] single-qubit erasures')
    def coords(z):
        c=[sp.re(z[i,i]-z[3,3]) for i in range(3)]
        for i in range(4):
            for j in range(i+1,4): c += [sp.re(z[i,j]),sp.im(z[i,j])]
        return c
    cols=[]
    for p in range(12):
        for l in range(4):
            E=sp.zeros(12,4); E[p,l]=1
            for phase in (1,I):
                X=W*(phase*E); out=[]
                for M in ops: out += coords(X.H*M*V+V.H*M*X)
                cols.append(sp.Matrix(out))
    J=sp.Matrix.hstack(*cols)
    orbit=[]
    for H in ops:
        z=W.H*(-I*H)*V; c=[]
        for p in range(12):
            for l in range(4): c += [sp.re(z[p,l]),sp.im(z[p,l])]
        orbit.append(sp.Matrix(c))
    O=sp.Matrix.hstack(*orbit)
    print('\n3. [[4,2,2]] exact stacked Jacobian:', J.rank(), J.cols-J.rank(), O.rank())
    assert J.rank()==84 and J.cols-J.rank()==12 and O.rank()==12 and J*O==sp.zeros(J.rows,O.cols)


def exact_513():
    pos=['00000','10010','01001','10100','01010','00101']
    neg=['11011','00110','11000','11101','00011','11110','01111','10001','01100','10111']
    v0=sp.zeros(32,1)
    for s in pos: v0[int(s,2)]=sp.Rational(1,4)
    for s in neg: v0[int(s,2)]=-sp.Rational(1,4)
    v1=sp.zeros(32,1)
    for i in range(32):
        if v0[i]!=0: v1[i^31]=v0[i]
    V=sp.Matrix.hstack(v0,v1)
    Wcols=[]; local=[]
    for q in range(5):
        for pc in 'XYZ':
            s=['I']*5; s[q]=pc; H=spauli(''.join(s)); local.append(H); Wcols += [H*V[:,0],H*V[:,1]]
    W=sp.Matrix.hstack(*Wcols)
    assert W.H*W==sp.eye(30) and W.H*V==sp.zeros(30,2)
    Lops=[X2,Y2,Z2]; rows=[]
    erasure_ops=[]
    for R in itertools.combinations(range(5),2):
        for chars in itertools.product('IXYZ',repeat=2):
            if chars==('I','I'): continue
            s=['I']*5
            for q,c in zip(R,chars): s[q]=c
            erasure_ops.append(spauli(''.join(s)))
    assert_scalar_compressions_exact(V,erasure_ops,'[[5,1,3]] two-qubit erasures')
    for Mfull in erasure_ops:
        M=W.H*Mfull*V
        for Q in Lops:
            row=[]
            # variable order: real block, then imaginary block
            for imag in (False,True):
                c=I if imag else 1
                for u in range(30):
                    for j in range(2):
                        D=sp.zeros(2,2)
                        for kk in range(2):
                            D[j,kk]+=sp.conjugate(c)*M[u,kk]
                            D[kk,j]+=sp.conjugate(M[u,kk])*c
                        row.append(sp.expand(sp.trace(Q*D)))
            rows.append(row)
    J=sp.Matrix(rows)
    orbit=[]
    for H in local:
        z=W.H*(-I*H*V); vec=[]
        for imag in (False,True):
            for u in range(30):
                for j in range(2): vec.append(sp.im(z[u,j]) if imag else sp.re(z[u,j]))
        orbit.append(sp.Matrix(vec))
    O=sp.Matrix.hstack(*orbit)
    r=J.rank(); ro=O.rank()
    print('4. [[5,1,3]] exact stacked Jacobian:', r, J.cols-r, ro)
    assert r==105 and J.cols-r==15 and ro==15 and J*O==sp.zeros(J.rows,O.cols)

# ---------- numerical Steane contrast ----------
NP={'I':np.eye(2,dtype=complex),'X':np.array([[0,1],[1,0]],complex),'Y':np.array([[0,-1j],[1j,0]],complex),'Z':np.diag([1,-1]).astype(complex)}
def npauli(s):
    M=np.array([[1]],complex)
    for c in s: M=np.kron(M,NP[c])
    return M

def stabilizer_basis(n,gens):
    P=np.eye(2**n,dtype=complex)
    for g in gens: P=P@(np.eye(2**n)+npauli(g))/2
    val,vec=np.linalg.eigh((P+P.conj().T)/2); return vec[:,val>.5]

def null_complement(V):
    u,s,vh=np.linalg.svd(V.conj().T,full_matrices=True); return vh.conj().T[:,V.shape[1]:]

def np_logical_basis(K):
    return hermitian_basis(K,True)

def np_stacked(V,n,regions):
    N,K=V.shape; W=null_complement(V); m=W.shape[1]; LB=np_logical_basis(K); rows=[]
    for R in regions:
        for chars in itertools.product('IXYZ',repeat=len(R)):
            if all(c=='I' for c in chars): continue
            ss=['I']*n
            for q,c in zip(R,chars): ss[q]=c
            M=W.conj().T@npauli(''.join(ss))@V
            for Q in LB:
                row=[]
                for imag in (False,True):
                    c=1j if imag else 1
                    for u in range(m):
                        for j in range(K):
                            D=np.zeros((K,K),complex); D[j,:]+=np.conj(c)*M[u,:]; D[:,j]+=c*np.conj(M[u,:])
                            row.append(np.trace(Q@D).real)
                rows.append(row)
    return np.asarray(rows),W

def steane_numeric():
    V=stabilizer_basis(7,['XXXXIII','XXIIXXI','XIXIXIX','ZZZZIII','ZZIIZZI','ZIZIZIZ'])
    regions=list(itertools.combinations(range(7),2))
    erasure_ops=[]
    for R in regions:
        for chars in itertools.product('IXYZ',repeat=len(R)):
            if all(c=='I' for c in chars): continue
            ss=['I']*7
            for q,c in zip(R,chars): ss[q]=c
            erasure_ops.append(npauli(''.join(ss)))
    assert_scalar_compressions_numeric(V,erasure_ops,'Steane [[7,1,3]] two-qubit erasures')
    J,W=np_stacked(V,7,regions)
    rank=np.linalg.matrix_rank(J,tol=1e-9)
    orbit=[]
    for q in range(7):
        for pc in 'XYZ':
            s=['I']*7; s[q]=pc; z=W.conj().T@(-1j*npauli(''.join(s))@V); vec=[]
            for imag in (False,True):
                for u in range(W.shape[1]):
                    for j in range(2): vec.append(z[u,j].imag if imag else z[u,j].real)
            orbit.append(vec)
    O=np.asarray(orbit).T; ro=np.linalg.matrix_rank(O,tol=1e-9)
    print('5. Steane numerical stacked Jacobian:', rank, J.shape[1]-rank, ro, '||JO||=',np.linalg.norm(J@O))
    assert rank==294 and J.shape[1]-rank==210 and ro==21 and np.linalg.norm(J@O)<1e-9

if __name__=='__main__':
    verify_covariance_theorems(); verify_leakage(); exact_422(); exact_513(); steane_numeric()
    print('\nALL CHECKS PASSED')
