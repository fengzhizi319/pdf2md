## – Understanding Lasso A Novel Lookup Argument Protocol 

Oleg Fomenko Anton Levochko Distributed Lab Distributed Lab oleg.fomenko@distributedlab.com anton.levochko@distributedlab.com 

## **Abstract** 

In 2023, Srinath Setty, Justin Thaler, and Riad Wahby published a paper that describes a novel lookup argument with efficient verification called Lasso. We present a focused and accessible overview of the Lasso lookup argument that stands for the foundational component of the Jolt ZK-VM. This article distills the core principles behind Lasso: the sum-check protocol, multilinear polynomials and their extensions, Spark commitment, offline memory-checking, and the evolution of Spark called Surge. By clarifying the underlying protocols and their relationship to innovations like Spark and Surge, we aim to provide researchers and engineers with practical insights into the cryptographic foundations powering both Lasso and the Jolt virtual machine. 

## **1 Introduction** 

This document presents a clear, streamlined overview of the Lasso lookup argument, first introduced in [STW23]. At its core, Lasso is a family of lookup arguments that enables efficient verification of “out-of-circuit” table lookups, crucial for stateful and memory-heavy computations. It serves as the centerpiece of Jolt, a ZK-VM designed by the a16zCrypto team. Our goal is to make the underlying protocol more accessible by concentrating on its core component: the cryptographic commitment to a large, sparse matrix. We hope this concise treatment will serve as a practical guide for researchers and engineers seeking to understand the cryptographic foundations of both Lasso and Jolt. 

Firstly, we begin by examining the lookup protocol. Suppose that the verifier has a commitment to a table _t ∈_ F _[n]_ as well as a commitment to another vector _a ∈_ F _[m]_ . Suppose that a prover wishes to prove that all entries in _a_ are in the table _t_ . There is a simple, commonly known way to prove this statement: prove the existence of a matrix _M ∈_ F _[m][×][n]_ where each row has only one non-zero element (namely the 1) such that the following statement works: 

**==> picture [41 x 7] intentionally omitted <==**

We call such matrix _M_ a **unit-row matrix** . This statement can be easily verified by proving that for a random row _r_ selected by the verifier, the following holds: 

**==> picture [53 x 11] intentionally omitted <==**

where _Mr_ denotes the _r_ -th row and _ar_ denotes _r_ -th element of _a_ . More precisely, in Lasso, the prover provides a commitment to the multilinear extensions of matrix _M_ and vectors _a, t_ that enables this check for a random coin _r ∈_ F _[m]_ up to a negligible soundness error (following Schwartz–Zippel lemma): 

**==> picture [133 x 25] intentionally omitted <==**

where _r_ and _y_ denote row and column indexes of the matrix. 

The main magic happens in the way Lasso commits to the multilinear extension of matrix _M_ and provides the opening at random row _r_ . While the matrix _M_ is naturally sparse, Lasso [STW23] presents **Spark** and its extension called **Surge** that allows us to commit to the sparse matrix _M_ efficiently. 

In the paragraphs below, we focus on the Spark construction and foundational protocols such as the sum-check protocol and the offline memory check. We also describe the Sona multilinear polynomial commitment, which is referenced as the primary commitment method in the original paper. Finally, after presenting Spark and its underlying components, we describe Surge – a generalization of Spark – and introduce some notes about the Spark protocol complexity. 

1 

## **2 Basic Knowledge** 

This section introduces the key protocols and concepts necessary to understand how Lasso works. Most of the definitions are adapted from [Tha22] with minor modifications; refer to it for more detailed explanations. We assume that the reader is already acquainted with fundamental cryptographic primitives (including commitment schemes, oracle access, and interactive proof systems) as well as core concepts from linear algebra (such as groups, fields, and polynomials). 

## **2.1 Multilinear Polynomial** 

We call an _ℓ_ -variate polynomial _f_ : F _[ℓ] →_ F **multilinear** if it has degree at most one in each variable. Let _f_ : _{_ 0 _,_ 1 _}[ℓ] →_ F be any function mapping the _ℓ_ -dimensional boolean hypercube to a field F. By definition, it equals 

**==> picture [89 x 25] intentionally omitted <==**

For _f_ we can observe an equivalence between the notions of a “multilinear polynomial” and “ordered list”. Indeed, any _ℓ_ -variate multilinear polynomial _f_ can be represented as a vector of 2 _[ℓ]_ elements, where the element at position _i_ =[�] _[ℓ] j[−]_ =0[1][2] _[j][ ·][r][j]_[equals to the] _[ f]_[(] _[r]_[0] _[, . . . , r][ℓ][−]_[1][).][This list can be naturally expressed] as 

**==> picture [338 x 11] intentionally omitted <==**

where the arguments are lexicographically ordered. To perform the inverted transformation, we can define the equality function eq: _{_ 0 _,_ 1 _}[ℓ] × {_ 0 _,_ 1 _}[ℓ] →_ F as follows: 

**==> picture [284 x 31] intentionally omitted <==**

If we can represent this function as a polynomial, then we can build a multilinear polynomial from our array _t_ as follows (here, the notation _t_ [ _i_ ] denotes the _i_ -th element of the array _t_ ): 

**==> picture [299 x 33] intentionally omitted <==**

**Remark 1.** Here, we used the notation[�] 2 _[j] xj_ to denote the conversion from a binary string to its corresponding value in F. For simplicity, in the remainder of this document, we will generally omit this explicit notation and assume that the conversion from a binary array _x_ to its value in F is performed. 

**Remark 2.** Since we’ve shown the equivalence between ordered lists and multilinear polynomials, we will henceforth treat these terms as interchangeable on both the prover’s and verifier’s sides. In particular, we assume that any multilinear polynomial can be accessed in either of these two forms (and their derivative forms) at any time. 

## **2.2 Multilinear Extension (MLE)** 

We say that _f_[�] : F _[ℓ] →_ F **extends** _f_ : _{_ 0 _,_ 1 _}[ℓ] →_ F if _f_[�] ( _x_ ) = _f_ ( _x_ ) for all _x ∈{_ 0 _,_ 1 _}[ℓ]_ . The total degree of an _ℓ_ -variate polynomial _f_ refers to the maximum sum of the exponents in any monomial of _f_ . Observe that if the _ℓ_ -variate polynomial _f_ is multilinear, then its total degree is at most _ℓ_ . It is well-known that for any _f_ , there is a unique multilinear polynomial _f_[�] that extends _f_ . The polynomial _f_[�] is referred to the **multilinear extension (MLE)** of _f_ . 

A particular multilinear extension that arises frequently in the design of proof systems is eq,� which is the MLE of the function eq: _{_ 0 _,_ 1 _}[ℓ] × {_ 0 _,_ 1 _}[ℓ] →_ F defined in Equation (1). An explicit expression for eq� is: 

**==> picture [311 x 30] intentionally omitted <==**

Indeed, one can easily check that the right hand side of Equation (2) is a multilinear polynomial, and that if evaluated at any input ( _x, e_ ) _∈{_ 0 _,_ 1 _}[ℓ] × {_ 0 _,_ 1 _}[ℓ]_ , it outputs 1 if _x_ = _e_ and 0 otherwise. Hence, the 

2 

right-hand side of Equation (2) is the unique multilinear polynomial extending eq. Equation (2) implies that eq(� _r_ 1 _, r_ 2) can be evaluated at any point ( _r_ 1 _, r_ 2) _∈_ F _[ℓ] ×_ F _[ℓ]_ in _O_ ( _ℓ_ ) time. This polynomial is also called a **Lagrange basis polynomial** for _ℓ_ -variate multilinear polynomial. 

## **2.3 Sona: Multilinear Polynomial Commitment Scheme** 

Throughout this article walkthrough, the discussed protocols relied on oracle access to the polynomials generated by the prover. So, we began by specifying the required type of oracle access: a cryptographic commitment to multilinear polynomials. This allowed us to finally define the concrete scheme presented in [STW23], known as **Sona** . It builds on top of the Hyrax protocol from [Wah+18] and the Nova framework [KST22], introducing a simplified, non-zero-knowledge variant of Hyrax called BabyHyrax, which is then integrated into Nova’s zero-knowledge setting. 

Note that, in general, the Lasso protocol does not restrict the usage of a certain multilinear polynomial commitment scheme. For example, the implementation of Lasso in Jolt ZK-VM currently leverages a KZG-based polynomial commitment for multilinear polynomials. One may note that the selected commitment protocol affects the prover and verifier complexity directly. 

## **2.3.1 BabyHyrax** 

We start by defining a non-zero-knowledge version of Hyrax multilinear polynomial commitment called BabyHyrax. In this section, we define the commitment itself and the protocol to evaluate a committed _ℓ_ -variate multilinear polynomial at a random point _r ∈{_ 0 _,_ 1 _}[ℓ]_ sampled by the verifier in a non-zeroknowledge environment. 

Let’s put _f_ : _{_ 0 _,_ 1 _}[ℓ] →_ F an _ℓ_ -variate multilinear polynomial. Instead of observing its coefficients, the commitment scheme works with the witness vector _t ∈_ F[2] _[ℓ]_ , where _tr_ = _f_ ( _r_ ) for each _r ∈{_ 0 _,_ 1 _}[ℓ]_ (in other words – the ordered list representation of our multilinear polynomial). For simplicity, we put 2 _[ℓ]_ = _m_ . We start by restructuring the witness vector _t_ of size _m_ into a matrix _T_ of size _[√] m ×[√] m_ . Then, using the vector Pedersen commitment in group G with generators _g_ 0 _, . . . , g_ ~~_[√]_~~ _m−_ 1[,][we][commit][to][the][rows][of] this matrix: 

**==> picture [66 x 33] intentionally omitted <==**

The resulting commitment will be a hash of vector _c_ : 

**==> picture [115 x 13] intentionally omitted <==**

Now, we can consider the opening protocol. First of all we redefine the polynomial _f_ using the witness vector _t_ for the query point _r ∈{_ 0 _,_ 1 _}[ℓ]_ , using the Lagrange basis polynomial: 

**==> picture [289 x 33] intentionally omitted <==**

The last product can be rewritten as follows: 

**==> picture [427 x 34] intentionally omitted <==**

Then, we define: 

**==> picture [151 x 68] intentionally omitted <==**

So, we can replace the eq� by multiplication of _u_ and _v_ (where _kl_ and _kr_ define the left and right halves of _k_ ): 

**==> picture [80 x 11] intentionally omitted <==**

3 

Thus, our original equation changes as follows: 

**==> picture [405 x 37] intentionally omitted <==**

where _w_ = ( _w_ 0 _, . . . , w_ ~~_[√]_~~ _m−_ 1[)][and] _[w][j]_[=][ �] _i∈_ [ ~~_[√]_~~ _m_ ] _[T][i,j][·][ u][i]_[.] 

Observe that for each _i ∈_ [ _[√] m_ ], a Pedersen commitment to _wi_ can be obtained by raising _ci_ to the exponent _ui_ . In particular, 

**==> picture [191 x 38] intentionally omitted <==**

In the original Hyrax, the prover runs a Bulletproof protocol instance to prove the inner product _⟨w, v⟩_ = _f_ ( _r_ ) using a commitment to _wi_ . In the BabyHyrax, instead, we send the _w_ to the verifier as it is (assuming that the protocol does not need to be zero-knowledge or that it will be used in a zero-knowledge environment). 

## **2.3.2 Sona** 

So, for an _ℓ_ -variate multilinear polynomial _f_ : _{_ 0 _,_ 1 _}[ℓ] →_ F the commitment and the evaluation proof consists of: 

**==> picture [133 x 30] intentionally omitted <==**

The original Sona leverages the Nova backend [KST22] to prove that the following relation holds for the arbitrary point _r_ and prover answer _v[⋆]_ = _f_ ( _r_ ): 

**==> picture [154 x 57] intentionally omitted <==**

Following the definition of Sona commitment protocol, we can describe a bunch of functions that leverage an arbitrary collision-resistant hash function Hash : G ~~_√_~~ _m →_ F, a Nova prover ProveNova and a verifier VerifyNova functions, and generator points _g ∈_ G ~~_√_~~ _m_ : 

CommitSona( _f_ : _{_ 0 _,_ 1 _}[ℓ] →_ F) 1: Put _m_ = 2 _[ℓ]_ 2: Evaluate witness vector _t ∈_ F _[m]_ from _f_ and restructure it into the matrix T. 3: **for** _i ←_ 0 **to** _[√] m −_ 1 **do** 4: _ci ←_[�] ~~_[√]_~~ _j_ =0 _m−_ 1 _gj[T][i,j] ∈_ G 5: **end for** 6: _Cf ←_ Hash( _c_ 0 _, . . . , c_ ~~_[√]_~~ _m−_ 1[)] 7: **return** _Cf_ 

OpenSona( _Cf ∈_ F, _r ∈{_ 0 _,_ 1 _}[ℓ]_ ) 1: Put _m_ = 2 _[ℓ]_ 2: For each _k ∈{_ 0 _,_ 1 _}[ℓ/]_[2] derive _u_ and _v_ according to BabyHyrax: 

**==> picture [150 x 31] intentionally omitted <==**

4 

**==> picture [142 x 32] intentionally omitted <==**

3: _// While u and v vectors seem to be calculated in O_ (2 _[ℓ/]_[2] ) _time, they consume only O_ (1) _because of an obvious structure_ . 4: **for** _j ←_ 0 **to** _[√] m −_ 1 **do** 5: _// It is assumed that we can obtain a witness matrix T from memory for the queried commitment Cf_ . 6: _wj ←_[�] ~~_[√]_~~ _i_ =0 _m−_ 1 _Ti,j ui_ 7: **end for** 8: _v[⋆] ←⟨w, v⟩ // Remember that ⟨w, v⟩_ = _f_ ( _r_ ) 9: _π ←_ ProveNova( _c_ 0 _, . . . , c_ ~~_[√]_~~ _m−_ 1 _[, T][|][C][f][, r, u, v, v][⋆]_[)] 10: **return** ( _v[⋆] , π_ ) 

VerifySona( _Cf ∈_ F, _r ∈{_ 0 _,_ 1 _}[ℓ]_ , _v[⋆]_ , _π_ ) 

1: For each _k ∈{_ 0 _,_ 1 _}[ℓ/]_[2] derive _u_ and _v_ according to BabyHyrax: 

**==> picture [150 x 73] intentionally omitted <==**

2: _// While u and v vectors seem to be calculated in O_ (2 _[ℓ/]_[2] ) _time, they consume only O_ (1) _because of an obvious structure_ . 3: **if** VerifyNova( _Cf , r, u, v, v[⋆] , π_ ) = **True then** 4: _V_ **rejects** 5: **end if** 

Thus, the evaluation of an oracle access “open” function at some point consists of a combined running of OpenSona and VerifySona, which is preceded by a single run of CommitSona. Also, one can note that the protocol environment strictly fixes the degree of the polynomial (i.e., multilinear polynomial). 

## **2.4 Sum-Check Protocol** 

A sum-check protocol [Lun+92] is an interactive proof protocol used in theoretical computer science to verify the correctness of a sum of values computed by a multivariate polynomial over a finite field, while having oracle access to the aforementioned polynomial. It allows a verifier to check a complex computation (like a huge sum over an exponential number of values) by interacting only a few times with a prover and doing logarithmic work. More precisely, let _g_ be some _ℓ_ -variate polynomial defined over a finite field F. The purpose of the sum-check protocol is for _V_ to make sure that the prover _P_ has calculated the following sum correctly (the definition below is taken from [Tha17]): 

**==> picture [76 x 25] intentionally omitted <==**

During the protocol walkthrough, we assume that _V_ has oracle access to the polynomial _g ∈_ F _[ℓ]_ [ _x_ ]. The protocol looks as follows: 

1. At the beginning of the protocol, the prover sends a value _C_ 1 claimed to equal the value _H_ . 

2. In the first round, _P_ sends to _V_ a univariate polynomial _g_ 1( _X_ 1) with the following construction: 

**==> picture [190 x 24] intentionally omitted <==**

5 

The sum in this polynomial is already computed by _P_ , so _V_ can evaluate it with _O_ (1) complexity. Then, _V_ checks that _C_ 1 = _g_ 1(0) + _g_ 1(1) and that _g_ 1 is a univariate polynomial of degree at most deg1( _g_ ), rejecting if not. 

3. _V_ chooses a random element _r_ 1 _∈_ F, and sends _r_ 1 to _P_ . 

4. In the _j_ th round, for 1 _< j < ℓ_ , _P_ sends _V_ a univariate polynomial _gj_ ( _Xj_ ) with the following construction: 

**==> picture [262 x 25] intentionally omitted <==**

_V_ checks that _gj_ is a univariate polynomial of degree at most deg _j_ ( _g_ ), and that _gj−_ 1( _rj−_ 1) = _gj_ (0) + _gj_ (1), rejecting if not. 

5. _V_ chooses a random element _rj ∈_ F, and sends _rj_ to _P_ . 

6. In Round _ℓ_ , _P_ sends _V_ a univariate polynomial _gℓ_ ( _Xℓ_ ) = _g_ ( _r_ 1 _, . . . , rℓ−_ 1 _, Xℓ_ ). _V_ checks that _gℓ_ is a univariate polynomial of degree at most deg _l_ ( _g_ ), rejecting if not, and also checks that _gℓ−_ 1( _rℓ−_ 1) = _gℓ_ (0) + _gℓ_ (1). 

7. _V_ chooses a random element _rℓ ∈_ F and evaluates _g_ ( _r_ 1 _, . . . , rℓ_ ) with a single oracle query to _g_ . _V_ checks that _gl_ ( _rℓ_ ) = _g_ ( _r_ 1 _, . . . , rℓ_ ), rejecting if not. 

8. If _V_ has not yet rejected, _V_ halts and accepts. 

While the definition of the protocol is universal, for future purposes, we need only a version that works with _ℓ_ -variate multilinear polynomials and leverages the Sona commitment protocol as an oracle access provider: 

Query( _Cf ∈_ F _, x_ : _{_ 0 _,_ 1 _}[ℓ]_ ) 1: _// This procedure is executed by both P and V_ 2: _P_ puts ( _f_ ( _x_ ) _, π_ ) _←_ OpenSona( _Cf_ , _x_ ) 

3: _V_ executes VerifySona( _Cf_ , _x_ , _f_ ( _x_ ), _π_ ) 

- 4: **return** _f_ ( _x_ ) 

Finally, we describe the sum-check algorithm, executed by both prover _P_ and verifier _V_ for the polynomial _g_ , its commitment _Cg_ , and the sum _H_ : 

SumCheckProtocol( _H ∈_ F _, g_ : _{_ 0 _,_ 1 _}[ℓ] →_ F, _Cg ∈_ F) 1: Put _g_ 1( _X_ 1) =[�] ( _x_ 2 _,...,xℓ_ ) _∈{_ 0 _,_ 1 _}[ℓ][−]_[1] _[ g]_[(] _[X]_[1] _[, x]_[2] _[, . . . , x][ℓ]_[).] 2: _P_ shares _g_ 1 with _V_ . 3: _V_ evaluates _g_ 1(0) and _g_ 1(1) 4: **if** _H_ = _g_ 1(0) + _g_ 1(1) **then** 5: _V_ **rejects** 6: **end if** 7: _V_ chooses a random element _r_ 1 _∈_ F, and evaluates _g_ 1( _r_ 1) 8: **for** _j ←_ 2 **to** _ℓ_ **do** 9: Put _gj_ ( _Xj_ ) =[�] ( _xj_ +1 _,...,xℓ_ ) _∈{_ 0 _,_ 1 _}[ℓ][−][j][ g]_[(] _[r]_[1] _[, . . . , r][j][−]_[1] _[, X][j][, x][j]_[+1] _[, . . . , x][ℓ]_[)] 10: _P_ shares _gj_ with _V_ . 11: _V_ evaluates _gj_ (0) and _gj_ (1) 12: **if** _gj−_ 1( _rj−_ 1) _̸_ = _gj_ (0) + _gj_ (1) **then** 13: _V_ **rejects** 14: **end if** 15: _V_ chooses a random element _rj ∈_ F, and evaluates _gj_ ( _rj_ ) 16: **end for** 17: _V_ puts _g_ ( _r_ 1 _, . . . , rℓ_ ) _←_ Query( _Cg_ , ( _r_ 1 _, . . . , rℓ_ )) 18: **if** _gℓ_ ( _rℓ_ ) _̸_ = _g_ ( _r_ 1 _, . . . , rℓ_ ) **then** 19: _V_ **rejects** 20: **end if** 

6 

**Remark.** Sometimes, _g_ is not committed directly; instead, it is specified as a predefined combination of other committed polynomials. In this case, **we override the query/commit methods by committing/querying these polynomials and combining them according to the pre-defined structure.** 

## **2.5 Sum-Check-based Protocol for Grand Products** 

Following [SL20], this subsection describes a transparent SNARK, which may be of independent interest, for proving grand product relations of the following form: 

**==> picture [171 x 29] intentionally omitted <==**

Let _m_ = _|V |_ . WLOG, assume that _m_ is a power of 2. Let _V_ denote a table of evaluations of a log _m_ - variate multilinear polynomial _v_ ( _x_ ) over _{_ 0 _,_ 1 _}_[log] _[ m]_ in a natural fashion. We assume the prover first opens _P_ and then commits to _v_ ( _x_ ); the ensuing protocol then verifies both the polynomial’s validity and the corresponding grand-product equality derived from that commitment. 

**Lemma 1.** _Following [SL20]:_ 

**==> picture [87 x 25] intentionally omitted <==**

_satisfied if and only if there exists a multilinear polynomial f in_ log _m_ +1 _variables such that f_ (1 _, . . . ,_ 1 _,_ 0) = _P and ∀x ∈{_ 0 _,_ 1 _}_[log] _[ m] the following hold:_ 

**==> picture [108 x 26] intentionally omitted <==**

_Such polynomial f has the following construction:_ 

**==> picture [75 x 11] intentionally omitted <==**

**==> picture [318 x 14] intentionally omitted <==**

Then, to check that _∀x ∈{_ 0 _,_ 1 _}_[log] _[ m]_ the equation _f_ (1 _, x_ ) = _f_ ( _x,_ 0) _· f_ ( _x,_ 1) holds, we can use a sum-check protocol to prove the evaluation of _g_ that is referred to a MLE of _f_ (1 _, x_ ) _− f_ ( _x,_ 0) _· f_ ( _x,_ 1): 

**==> picture [229 x 25] intentionally omitted <==**

By the Schwartz–Zippel lemma, except for a soundness error of[lo] _|_[g] F _[ m] |_ (which should be negligible), _g_ ( _τ_ ) = 0 for _τ_ uniformly random in F[log] _[ m]_ if and only if _g_ = 0, which implies that _f_ (1 _, x_ ) _− f_ ( _x,_ 0) _· f_ ( _x,_ 1) = 0 for all _x ∈{_ 0 _,_ 1 _}_[log] _[ m]_ . 

Similarly, to prove that _v_ ( _x_ ) = _f_ (0 _, x_ ) for all _x ∈{_ 0 _,_ 1 _}_[log] _[ m]_ it suffices to prove that _v_ ( _γ_ ) = _f_ (0 _, γ_ ) for a public coin _γ ∈_ F[log] _[ m]_ . 

Thus, to prove the existence of _f_ and hence the grand product relationship, it suffices to prove, for some verifier selected random _τ, γ ∈_ F _[ℓ]_ , that: 

**==> picture [336 x 25] intentionally omitted <==**

**==> picture [265 x 26] intentionally omitted <==**

This can be achieved by running the sum-check protocol between _P_ and _V_ , where _V_ has oracle access to _v_ and _f_ . Additionally, _V_ evaluates the _f, v_ at the random point _γ_ to verify that _f_ (0 _, x_ ) = _v_ ( _x_ ). So, the sum-check-based protocol for the grand products looks as follows: 

7 

GrandProductsProtocol( _V ∈_ F _[m] , P ∈_ F) 

- 1: _P_ compute polynomials _v ∈_ F[log] _[ m]_ [ _x_ ] _, f ∈_ F[log] _[ m]_[+1] [ _x_ ] such that _P_ =[�] _x∈{_ 0 _,_ 1 _}_[log] _[ m][ v]_[(] _[x]_[)][and] _[v, f]_ satisfies Equations (3), (4), (5). 

- 2: _P_ puts _Cf ←_ CommitSona( _f_ ) and _Cv ←_ CommitSona( _v_ ) and shares _Cf , Cv_ with _V_ . 3: _V_ chooses a random elements _τ, γ ∈_ F[log] _[ m]_ and sends _τ, γ_ to _P_ . 

- 4: _P_ puts _g[∗]_ ( _x_ ) = eq(� _x, τ_ ) _·_ ( _f_ (1 _, x_ ) _− f_ ( _x,_ 0) _· f_ ( _x,_ 1)) 

5: _P_ and _V_ run SumCheckProtocol(0, _g[∗]_ , _Cf_ ) _// We assume that the instance of the sum-check protocol here operates over commitment to f instead of the separate commitment to the input polynomial g[∗]_ 6: _V_ puts _f_ (1 _, . . ._ 1 _,_ 0) _←_ Query( _Cf_ , (1 _, . . . ,_ 1 _,_ 0)) 7: **if** _f_ (1 _, . . ._ 1 _,_ 0) _̸_ = _P_ **then** 8: _V_ **rejects** 9: **end if** 10: _V_ puts _f_ (0 _, γ_ ) _←_ Query( _Cf_ , (0 _, γ_ )) and _v_ ( _γ_ ) _←_ Query( _Cf_ , _γ_ ) 11: **if** _f_ (0 _, γ_ ) _̸_ = _v_ ( _γ_ ) **then** 12: _V_ **rejects** 13: **end if** 

We noted that during the call to the sum-check protocol, we pass the polynomial _g[∗]_ in a couple with the commitment to _f_ . Here we assume that each invocation of the Query method to _g[∗]_ inside the sum-check instance will be more complex: **instead of evaluating a single function and returning result, we evaluate** _f_ **at three different points, check the proofs and return results according to the construction of** _g[∗]_ . 

Also, note that the definition of _f_ strictly depends on the nature of _v_ (i.e, _V_ ). In the protocol that follows, we construct _V_ from commitments to several polynomials; evaluations of _f_ and _v_ are therefore carried out through oracle access to those committed polynomials, removing the need for separate commitments to _f_ and _v_ . Since we no longer have to commit to the _f_ , we do not need to build it for an arbitrary _v_ – instead, we can utilize its known structure to evaluate at a random point during the sum-check protocol: 

**==> picture [257 x 25] intentionally omitted <==**

So, the protocol can be modified as follows for future usage: 

1. We do not commit to _v_ directly – instead, we override its query function by querying the evaluation of certain, committed polynomials and combining them according to the pre-defined structure. 

2. We do not commit to _f_ directly and prover do not build _f_ directly – instead, we leverage the known structure of _f_ , evaluating it at certain points by querying _v_ at these points. 

## **2.6 Offline Memory Checking** 

The goal of the memory-checking protocol is to enable a verifier to audit a huge, untrusted memory transcript using only a tiny proof: the prover records every read, write, and the verifier checks with a single grand-product that the multiset of reads equals the multiset of writes plus the initial image. If the equality holds, then each read has returned the most recently written value. Using this approach, the verifier can ensure that the committed sparse-matrix vectors representing the unit-row matrix are properly structured, without ever scanning the entire memory. 

In the present version of this protocol, each operation is followed by an increment of the corresponding memory cell counter (unlike the original version, where the counter was global). The present protocol also utilizes only reads, pairing them with “synthetic” writes. The implementation of this protocol for Spark requires only three sets of tuples to work with: 

- WS – contains tuples that represent write operations: (addr _,_ val _,_ counteraddr), where val is the value stored at the memory address addr after the specified counter; 

- RS – contains tuples that represent read operations: (addr _,_ val _,_ counteraddr), where val is the value read from the memory address addr at the specified counter; 

8 

- S – contains tuples such that WS = RS _∪_ S if and only if all operations were executed correctly; otherwise, no such S exists that satisfies this equality. 

You can think of a memory as a vector of values, and a counter as a memory cell timestamp, separately for read and write operations. At the beginning, WS is populated with the initial memory state, where all counters are set to 0, indicating that the values were first accessed during the initialization phase, while the RS _,_ S are empty. Then, for each read operation, the untrusted memory is queried at addr, returning a pair (val _,_ counter). The tuple (addr _,_ val _,_ counter) is written in RS, and a corresponding write operation (addr _,_ val _,_ counter + 1) is added to WS. After all the read operations are done, one can notice that S equals the final memory state. The equality of multisets WS and RS _∪_ S can be verified by a single grand-product check. 

**Claim 1** ([STW23] Randomized Permutation Check) **.** _Let A and B be two multisets of tuples in_ F[3] _. Define_ 

**==> picture [325 x 24] intentionally omitted <==**

_Then comparing Hτ,γ_ ( _A_ ) _and Hτ,γ_ ( _B_ ) _yields a randomized test for whether A and B are permutations of one another. Concretely: 1. If A_ = _B (as multisets), then_ 

**==> picture [85 x 11] intentionally omitted <==**

_with probability 1 over uniform τ, γ ∈_ F _. 2. If A ̸_ = _B, then_ 

**==> picture [206 x 13] intentionally omitted <==**

_In other words, by first “hashing” each tuple via the map function hγ and then taking the τ -shifted product, one obtains a fingerprint that is invariant under permutation but unlikely to collide on distinct multisets._ 

Thus, WS = RS _∪_ S can be written as: 

**==> picture [409 x 71] intentionally omitted <==**

**Example (** _N_[1] _[/c]_ = 4 _, m_ = 3 **)** 

We track a single _row-memory_ . The algorithm performs three reads. 

Address 0 1 2 3 Value 2 5 7 9 

**Initial memory (counter** 0 **):** WSinit = _{_ (0 _,_ 2 _,_ 0) _,_ (1 _,_ 5 _,_ 0) _,_ (2 _,_ 7 _,_ 0) _,_ (3 _,_ 9 _,_ 0) _}_ , while RS = ∅ and S = ∅ are both empty. 

**Trace 1 – consistent execution** 

**step operation** ∆RSstep ∆WSstep 1 read(1) _→_ (5 _,_ 0) (1 _,_ 5 _,_ 0) (1 _,_ 5 _,_ 1) 2 read(0) _→_ (2 _,_ 0) (0 _,_ 2 _,_ 0) (0 _,_ 2 _,_ 1) 3 read(2) _→_ (7 _,_ 0) (2 _,_ 7 _,_ 0) (2 _,_ 7 _,_ 1) After the three steps RS = _{_ (1 _,_ 5 _,_ 0) _,_ (0 _,_ 2 _,_ 0) _,_ (2 _,_ 7 _,_ 0) _},_ WS = WSinit _∪{_ (1 _,_ 5 _,_ 1) _,_ (0 _,_ 2 _,_ 1) _,_ (2 _,_ 7 _,_ 1) _}._ And we can fill S with S = _{_ (0 _,_ 2 _,_ 1) _,_ (1 _,_ 5 _,_ 1) _,_ (2 _,_ 7 _,_ 1) _,_ (3 _,_ 9 _,_ 0) _}_ 

9 

One can clearly see that WS = RS _∪_ S. 

_Hτ,γ_ (WS) = (1 _γ_[2] + 5 _γ_ + 0 _− τ_ ) (0 _γ_[2] + 2 _γ_ + 0 _− τ_ ) (2 _γ_[2] + 7 _γ_ + 0 _− τ_ ) � �� � _Hτ,γ_ (RS) _×_ (0 _γ_[2] + 2 _γ_ + 1 _− τ_ ) (1 _γ_[2] + 5 _γ_ + 1 _− τ_ ) (2 _γ_[2] + 7 _γ_ + 1 _− τ_ ) (3 _γ_[2] + 9 _γ_ + 0 _− τ_ ) � �� � _Hτ,γ_ (S) = _Hτ,γ_ (RS) _× Hτ,γ_ (S) _._ 

## **Trace 2 – inconsistent execution** 

Let the second reading return a wrong value – _a_ , instead of 2. So, the new trace would look like: 

After the three steps 

**step operation** ∆RSstep ∆WSstep 1 read(1) _→_ (5 _,_ 0) (1 _,_ 5 _,_ 0) (1 _,_ 5 _,_ 1) 2 read(0) _→_ ( _a,_ 0) (0 _, a,_ 0) (0 _, a,_ 1) 3 read(2) _→_ (7 _,_ 0) (2 _,_ 7 _,_ 0) (2 _,_ 7 _,_ 1) RS = _{_ (1 _,_ 5 _,_ 0) _,_ (0 _, a,_ 0) _,_ (2 _,_ 7 _,_ 0) _},_ WS = WSinit _∪{_ (1 _,_ 5 _,_ 1) _,_ (0 _, a,_ 1) _,_ (2 _,_ 7 _,_ 1) _},_ S _→_ does not exist 

Now, RS contains (0 _, a,_ 0) while WS still contains the untouched initial tuple (0 _,_ 2 _,_ 0). No multiset S that depends on the valid values and addresses can reconcile them, and the verifier _rejects_ . 

## **3 Spark Commitment Protocol** 

Spark is a sparse polynomial commitment scheme. It allows an untrusted prover to prove evaluations of a sparse multilinear polynomial with costs proportional to the size of the dense representation of the sparse multilinear polynomial. 

It was originally introduced in the Spartan [Set19] as a tool for committing to R1CS matrices _A, B, C_ , which are inherently **sparse** (it contains much more zero values then non-zero), effectively reducing the prover’s commitment work by committing to _m_ non-zero elements instead of the full matrix. 

## **3.1 Multilinear Extension of Matrix** 

Firstly, we start from the MLE of a square matrix without any restrictions on the values inside. These assumptions will be changed in the next sections to fit the Lasso matrix format. Let _D ∈_ F _[M][×][M]_ be a sparse matrix over the field F. For convenience in some of the upcoming transitions, we can view it as a function _D_ ( _i, j_ ): F[2] _→_ F. Let’s define a polynomial that returns elements of our matrix by its indexes: 

**==> picture [203 x 32] intentionally omitted <==**

Here, eq( _a, b_ ): F[2] _−→{_ 0 _,_ 1 _}_ stands for the equality-check function that returns 1 if _a_ = _b_ , and 0 otherwise. These functions serve as Lagrange basis polynomials, ensuring that the expression evaluates to _D_ ( _i, j_ ) at the point ( _ri, rj_ ) = ( _i, j_ ), and zero elsewhere. Consequently, evaluating the sum, we receive the desired matrix value at the specified indices. 

Utilizing the eq� introduced in the MLE subsection we can build MLE of _D_ in the following way, assuming that _ri, rj ∈{_ 0 _,_ 1 _}_[log] _[ M]_ : 

**==> picture [263 x 25] intentionally omitted <==**

As a drawback, we would need to go through all the _M_[2] cells with this option, which is pretty inefficient. 

10 

Since _D_ is sparse, let us denote _m_ as the number of non-zero entries in the matrix. These non-zero entries can be represented as an array of tuples: _T_ = _{_ ( _ik, jk, D_ ( _ik, jk_ )) : _k_ = 0 _,_ 1 _, . . . , m −_ 1 _}_ . 

It can also be represented as three polynomials _row, col, val_ : _{_ 0 _,_ 1 _}_[log(] _[m]_[)] _→{_ 0 _,_ 1 _}_[log(] _[M]_[)] such that for each _k ∈_ [ _m_ ] a tuple ( _row_ ( _k_ ) _, col_ ( _k_ ) _, val_ ( _k_ )) _∈ T_ identifies a valid non-zero element of our initial matrix _D_ . With this structure, we can refactor our previous definition: 

**==> picture [255 x 25] intentionally omitted <==**

The usage of such polynomials to represent our matrix describes the basic idea behind the Spark commitment protocol: _if the matrix contains a lot of zeros, we can replace commitment to the matrix with commitment to several polynomials that describe the positions of non-zero elements_ . 

## **3.2 Eliminating the Logarithmic Factor** 

The section above describes how one can build an _m_ -sparse log _M_ -variate polynomial representation of a sparse matrix at a cost of its dense representation. This section describes a technique to eliminate the log _m_ factor during the polynomial evaluation. 

During the current iteration of the protocol description, we assume that the matrix we want to commit to has only one non-zero element per row equal to 1 (or, in other words, all rows are unit vectors). This simplification will allow us to avoid an unnecessary commitment to the _val_ polynomial (we know its values at all interesting points). Then, each non-zero element of the _M × N_ matrix can be represented as a pair of coordinates ( _i, j_ ) _∈_ [ _M_ ] _×_ [ _N_ ]. 

## **3.2.1 The Idea** 

**Naive evaluation.** Let _Li, i ∈_ [ _M_ ] be log _N_ -variate Lagrange-basis polynomials with, consequently, log _N_ evaluation cost, and _r ∈{_ 0 _,_ 1 _}_[log] _[ N]_ , then _L_ = _L_ 1( _r_ ) + _L_ 2( _r_ ) + _· · ·_ + _LM_ ( _r_ ) is a log _N_ -variate, _M_ -sparse polynomial that can be evaluated with a total cost of _O_ ( _M_ log _N_ ). 

**Eliminating the logarithmic factor.** The goal is to achieve _O_ ( _c · M_ ) evaluation time by ensuring that each Lagrange basis polynomial can be evaluated in _O_ ( _c_ ). Let’s decompose the log _N_ = _c ·_ log _m_ variables of _r_ into _c_ blocks, each of size log _m_ , writing _r_ = ( _r_ 1 _, . . . , rc_ ) _∈_ (F[log] _[ m]_ ) _[c]_ . Then any log _N_ -variate Lagrange basis polynomial evaluated at _r_ can be expressed as a product of _c_ “smaller” Lagrange basis polynomials, each defined over only log _m_ variables, with the _i_ ’th such polynomial evaluated at _ri_ . There are only 2[log] _[ m]_ = _m_ multilinear Lagrange basis polynomials over log _m_ variables, so, having _c_ inputs, one can evaluate all of them at each _ri_ in time _O_ ( _cm_ ), storing the result in a write-once memory. Now, given the memory, one can evaluate any given log _N_ -variate Lagrange basis polynomial at _r_ by performing _c_ lookups into the memory, one for each block _ri_ , and multiplying together the results, achieving _O_ ( _M · c_ ) total time for all the _M_ polynomials. 

It’s obvious, yet important to emphasize, that the choice of _c_ uniquely determines _m_ . While the parameter _c_ needs to be chosen in a way to ensure optimal calculations. 

## **3.2.2 Extending Matrix MLE** 

To apply the knowledge from the previous section, we need to encode a second coordinate of our _M × N_ matrix as a vector in a _c_ -dimensional hypercube, in effect decomposing a single log _N_ -variate polynomial 1 1 into smaller ones. This hypercube will have _c_ coordinates each of size _m_ = _N c_ giving us ( _N c_ ) _[c]_ = _N_ points in total. So, each _j ∈_ [ _N_ ] will be represented as a vector ( _j_ 0 _, . . . jc−_ 1), where _jk ∈_ [ _m_ ]. We also represent each hypercube coordinate as a binary vector of log _m_ elements, so each _j ∈_ [ _N_ ] will be encoded as ( _j_ 0 _, . . . jc−_ 1), where _jk ∈{_ 0 _,_ 1 _}_[log] _[ m]_ . 

Now, we can define the log _M_ -variate multilinear polynomials to represent the non-zero matrix elements, where the first coordinate stands for the evaluation point and the second coordinate stands for the evaluation point image: 

**==> picture [218 x 14] intentionally omitted <==**

So, for each _k ∈{_ 0 _,_ 1 _}_[log] _[ M]_ (goes through the all row indexes) vector ( _dim_ 1( _k_ ) _, . . . , dimc_ ( _k_ )) represents an encoded column index (in the hypercube coordinates) of a non-zero element in the row _k_ . 

11 

**==> picture [153 x 125] intentionally omitted <==**

1 Figure 1: Decomposing a column index _j ∈_ [ _N_ ] into a 2-dimensional ( _c_ = 2 _, m_ = _N_ 2 ) grid coordinate ( _j_ 0 _∈_ [ _m_ ] _, j_ 1 _∈_ [ _m_ ]) 

Thus, let’s put _r ∈{_ 0 _,_ 1 _}_[log] _[ M]_ as a row number, and _r[′]_ = ( _r_ 1 _[′][, . . . , r] c[′]_[),][where] _[r] i[′][∈{]_[0] _[,]_[ 1] _[}]_[log] _[ m]_[,][as][an] encoded column number, then: 

**==> picture [312 x 31] intentionally omitted <==**

where 

_∀k ∈{_ 0 _,_ 1 _}_[log] _[ M]_ : _Ei_ ( _k_ ) = eq(dim� _i_ ( _k_ ) _, ri[′]_[)] 

Here, eq(� _r, k_ ) stands for the MLE of the row-equality check function, as well as[�] _[c] i_ =1 _[E][i]_[(] _[k]_[) stands for the] column-equality check function. We also remove the value multiplier because of our initial assumption – non-zero elements in our matrix can only equal 1. 

**Conclusion.** This section describes an approach to encode the second matrix coordinate in the hypercube coordinates, which allows us to pre-calculate evaluations of small log _m_ -variate Lagrange basis polynomials eq� in _Ei_ ( _k_ ). The usage of the pre-calculated evaluations reduces the entire matrix MLE evaluation time by the log _m_ factor. More precisely, using the naive approach, the evaluation of _D_[�] ( _r, r[′]_ ) consists of the _M_ evaluation of log _N_ -variate polynomials, which consumes _O_ ( _M_ log _N_ ) time. The usage of the described approach requires _M_ evaluations of _c_ log _m_ -variate polynomials, but if all log _m_ -variate polynomial evaluations can be pre-computed and queried from memory with _O_ (1) complexity, the entire evaluation time will be _O_ ( _M · c_ ). 

## **3.3 Ensuring Consistency of Indicator Polynomials** 

Committing only to a dense matrix representation is a good performance boost, but it turns out that _dim_ 1 _, . . . , dimc_ and consequently, the indicator polynomials _Ei, i ∈_ [ _c_ ], can be easily made up to satisfy the equation. So, our goal now is to prove that the evaluation of _Ei_ follows from the correct pre-computed evaluations of eq� stored in both the prover’s and verifier’s memory and picked with correspondence to the _dimi_ . To address this issue, memory-checking techniques can be used to enforce consistency and correctness. 

� Remember _∀k ∈{_ 0 _,_ 1 _}_[log] _[ M]_ : _Ei_ ( _k_ ) = eq( _dimi_ ( _k_ ) _, ri[′]_[)] _[,][i][∈]_[[] _[c]_[].] Note that the proving of each _Ei_ consistency will be performed separately. So, while utilizing the memory checking approach, we need to define and commit to the vector of memory counter-s where the verifier will have an oracle access to them. For each _i ∈_ [ _c_ ] we put _M_ a number of read operations (obviously equals to the number of rows), and define the memory of size _m_ that contains the evaluations of all eq(� _j, ri[′]_[)][for][address] _[j]_[.][So,] the results of each eq(� _j, ri[′]_[)][as][well][as] _[E][i]_[(] _[j]_[)][are][strictly][fixed][by][the] _[dim][i]_[(] _[k]_[) =] _[ j]_[.][Additionally,][we][put] 

- _Cr ∈_ F _[M]_ – a vector of read-operation counters: _Cr_ [ _k_ ] contains the count that would have been returned by the untrusted memory if it were honest during the _k_ -th read operation 

- _Cf ∈_ F _[m]_ – a vector of final memory counters: _Cf_ [ _j_ ] stores the final count stored at memory location _j_ of the untrusted memory (if the untrusted memory were honest) at the termination of the _M_ read operations. 

12 

Let _read_ ~~_t_~~ _s_ = _C_[�] _r_ , _write_ ~~_t_~~ _s_ = _C_[�] _r_ + 1, _final_ ~~_c_~~ _ts_ = _C_[�] _f_ – we refer to these polynomials as counter polynomials, which are unique for a given memory and read operations. Note that _write_ ~~_t_~~ _s_ can be eliminated, as it can be derived from _read_ ~~_t_~~ _s_ with an increment. Therefore, we can build our multisets for the memory checking algorithm over _dimi, i ∈_ [ _c_ ] as follows: 

- 

- • WS _i_ = _{_ (to _-_ field( _j_ ) _,_ eq( _j, ri[′]_[)] _[,]_[ 0):] _[j][∈{]_[0] _[,]_[ 1] _[}]_[log] _[ m][}∪{]_[(] _[dim][i]_[(] _[k]_[)] _[, E][i]_[(] _[k]_[)] _[, read]_ ~~_t_~~ _si_ ( _k_ )+1): _k ∈{_ 0 _,_ 1 _}_[log] _[ M] }_ . As mentioned before, we initialize WS _i_ with the initial memory state and zero counters (the first subset). Then, for each read operation, we put its result in a couple with its address and the incremented counter (the second subset). 

- RS _i_ = _{_ ( _dimi_ ( _k_ ) _, Ei_ ( _k_ ) _, read_ ~~_t_~~ _si_ ( _k_ )): _k ∈{_ 0 _,_ 1 _}_[log] _[ M] }_ . During the evaluation of each _Ei_ ( _k_ ), we read from the memory a value at _dimi_ ( _k_ ) address that should be equal to the _Ei_ ( _k_ ) if the prover is honest. The reading counter strongly depends on the _dimi_ ( _k_ ) result. 

- 

- • S _i_ = _{_ (to _-_ field( _j_ ) _,_ eq( _j, ri[′]_[)] _[, final]_ ~~_c_~~ _tsi_ ( _j_ )): _j ∈{_ 0 _,_ 1 _}_[log] _[ m] }_ . To equalize our subsets, we have to add to the reading set the final counters of each memory cell _j ∈_ [ _m_ ]. Note that the memory cell value is fixed by the eq(� _j, ri[′]_[)][result.] 

Finally, we can check the equality WS _i_ = RS _i ∪_ S _i_ by running the sum-check-based protocol for grand products over _Hτ,γ_ (WS _i_ ) = _Hτ,γ_ (RS _i_ ) _· Hτ,γ_ (S _i_ ). 

**Grand Products Invocation.** For example, the verifier receives _P_ = _Hτ,γ_ (WS _i_ ) from prover and then both executes GrandProductsProtocol( _{hγ_ ( _a, v, t_ ) _− τ }|_ ( _a,v,t_ ) _∈_ WS _i_ , _P_ ). During the grand-products protocol, the verifier makes sure about the structure validity of the WS _i_ multiset by evaluating the _f_ and _v_ functions (see 2.5) at random points. As mentioned earlier (see 2.5), the _f_ and _v_ functions do not exist – instead, both the verifier and the prover know the structure of multiset WS _i_ , the evaluations of _hγ_ over its elements, and the resulting MLE of the input vector _{hγ_ ( _a, v, t_ ) _− τ }_ . So, instead of querying _f_ and _v_ directly, the verifier executes query requests to the committed polynomials _Ei_ , _dimi_ , _read_ ~~_t_~~ _si_ , and _final_ ~~_c_~~ _tsi_ , combining the results according to the multisets structure. 

## **3.4 Spark Commitment Algorithm** 

Finally, we can define the Spark commitment protocol procedure. The prover runs it over the unitrow matrix of size _M × N_ , encoding each non-zero element by _c_ polynomials _dim_ 1 _, . . . , dimc_ . Then, after committing to these polynomials, the prover provides the proof of the valid matrix decomposition, which includes both an evaluation of the matrix MLE at random coordinates and an instance of the memory check protocol to enable verification of the _Ei_ polynomials’ consistency. The evaluations of all eq� in _Ei_ are precomputed, so they consume _O_ (1) time. During the protocol, _V_ has oracle access to all polynomials via a Sona commitment protocol (more precisely, they are: _dim_ 1 _, . . . , dimc_ and _E_ 1 _, . . . , Ec_ and _read_ ~~_t_~~ _s_ 1 _, . . . , read_ ~~_t_~~ _sc_ and _final_ ~~_c_~~ _ts_ 1 _, . . . , final_ ~~_c_~~ _tsc_ ). 

CommitSpark(M : _{_ 0 _,_ 1 _}[M][×][N]_ ) 

- 1: _P_ executes CommitSona for _dim_ 1 _, . . . , dimc_ such that satisfy Equation (6) and shares the commitments with _V_ 

- 2: _V_ randomly chooses _r ∈_ [ _M_ ] and _r[′]_ = ( _r_ 1 _[′][, . . . , r] c[′]_[),][where] _[r] k[′][∈{]_[0] _[,]_[ 1] _[}]_[log] _[ m]_[and][sends] _[r, r][′]_[to] _[P]_ 3: _P_ executes CommitSona for _E_ 1 _, . . . , Ec_ and _read_ ~~_t_~~ _s_ 1 _, . . . , read_ ~~_t_~~ _sc_ and _final_ ~~_c_~~ _ts_ 1 _, . . . , final_ ~~_c_~~ _tsc_ and shares the commitments with _V_ 

- 4: _P_ opens to _V_ the value _y_ = _D_ ( _r, r[′]_ ) 

� 5: _P_ and _V_ run SumCheckProtocol _y_ , eq( _r, x_ ) _·_[�] _[c] i_ =1 _[E][i]_[(] _[x]_[)] _// We assume that the instance_ � � _of sum-check protocol here operates over commitments to Ei instead of the separate commitment to the input polynomial_ 6: _V_ chooses a random _τ, γ_ and sends them to _P_ 7: **for** _i ∈_ 1 _, . . . , c_ **do** 8: _P_ builds WS _i,_ RS _i_ and S _i_ multisets. 9: _P_ sends _V_ the evaluations of _Hτ,γ_ (WS _i_ ) _, Hτ,γ_ (RS _i_ ) and _Hτ,γ_ (S _i_ ) 10: _P_ and _V_ run GrandProductsProtocol� _{hγ_ ( _a, v, t_ ) _− τ }_ ��( _a,v,t_ ) _∈_ WS _i_[,] _[H][τ,γ]_[(][WS] _[i]_[)] � 11: _P_ and _V_ run GrandProductsProtocol� _{hγ_ ( _a, v, t_ ) _− τ }_ ��( _a,v,t_ ) _∈_ RS _i_[,] _[H][τ,γ]_[(][RS] _[i]_[)] � 

13 

12: _P_ and _V_ run GrandProductsProtocol� _{hγ_ ( _a, v, t_ ) _− τ }_ ��( _a,v,t_ ) _∈_ S _i_[,] _[H][τ,γ]_[(][S] _[i]_[)] � 13: **if** _Hτ,γ_ (WS _i_ ) _̸_ = _Hτ,γ_ (RS _i_ ) _· Hτ,γ_ (S _i_ ) **then** 14: _V_ **rejects** 15: **end if** 16: **end for** 

As mentioned before, the presented algorithm runs separate instances of the grand products protocol to check each _Ei_ consistency. But, by grouping _c_ multisets into a one multiset via a random linear combination, we can replace _c ×_ 3 grand product executions by only 3 executions. 

## **3.5 Example** 

Let’s show how the Lasso with Spark works on the matrix of size 4 _×_ 8. The vector _t_ will contain the following values: 

_t_ = (91 _,_ 24 _,_ 13 _,_ 45 _,_ 41 _,_ 38 _,_ 27 _,_ 23) 

Let’s put the _a_ = (91 _,_ 41 _,_ 91 _,_ 45). You can observe that the first value in it as well as the third appear at the first position in _t_ , the second appears at the fifth position in _t_ , and the last value appears at the fourth position. So, we can observe the following Lasso equation to be proven: 

**==> picture [203 x 97] intentionally omitted <==**

You can observe that the lookup matrix is sparse and unit-row, so we can encode using a polynomial that returns a column number by the row number: 

**==> picture [45 x 56] intentionally omitted <==**

According to the Spark notation, we have: _N_ = 8, log _N_ = 3 and _M_ = 4 _,_ log _M_ = 2. Let’s also put 1 1 _c_ = 3, then _m_ = _N c_ = 8 3 = 2. Thus, we are going to encode the column coordinate as a point at a 3-dimensional boolean hypercube of size 1. Let’s order its points (the ordering can be defined by the proving system in any way, but it should be the same on both verifier’s and prover’s side): 

**==> picture [223 x 156] intentionally omitted <==**

**----- Start of picture text -----**<br>
7: (0 ,  1 ,  1) 6: (1 ,  1 ,  1)<br>5: (1 ,  0 ,  1)<br>4: (0 ,  0 ,  1)<br>2: (1 ,  1 ,  0)<br>3: (0 ,  1 ,  0)<br>0: (0 ,  0 ,  0) 1: (1 ,  0 ,  0)<br>**----- End of picture text -----**<br>


14 

Then, we can rewrite the results of our _col_ polynomial as follows: 

_col_ (0) = 0 = (0 _,_ 0 _,_ 0) _col_ (1) = 4 = (0 _,_ 0 _,_ 1) _col_ (2) = 0 = (0 _,_ 0 _,_ 0) _col_ (3) = 3 = (0 _,_ 1 _,_ 0) 

Next, we initialize the _dimi, i ∈_ [ _c_ ] polynomials to represent each coordinate of the hypercube point: 

**==> picture [179 x 55] intentionally omitted <==**

After the prover commits to the _dimi_ polynomials, the verifier samples the challenge points _r_ and _r[′]_ for row and column. For example, let’s take _r_ = 1 _, r[′]_ = 4 (it can be any pair of coordinates, including the zero cells). More precisely, _r[′]_ = (0 _,_ 0 _,_ 1). Then, the prover and verifier initialize the memory with the evaluations of _Ei_ ( _k_ ) at each _k ∈{_ 0 _,_ 1 _}_[log] _[ M]_ = _{_ 0 _,_ 1 _}_[2] = [4]. For example, let’s observe the memory check � protocol for the _E_ 2 = eq( _dim_ 2( _k_ ) _, r_ 2 _[′]_[).][Firstly,][let’s][check][all][evaluations][of] _[E]_[2][(where] _[r]_ 2 _[′]_[= 0):] 

**==> picture [163 x 56] intentionally omitted <==**

� We have a memory of size _m_ = 2 with addresses 0 and 1 that stores eq( _j, r_ 2 _[′]_[)][for] _[j][∈]_[[] _[m]_[]][=][[2].][More] precisely, the initial memory looks as follows: 

**==> picture [83 x 39] intentionally omitted <==**

Thus, we can fill the WS2 _,_ RS2 _,_ S2 vectors: 

RS2 = _{_ ( _dim_ 2( _k_ ) _, E_ 2( _k_ ) _,_ read ~~t~~ s2( _k_ )): _k ∈{_ 0 _,_ 1 _}_[log] _[ M] }_ = _{_ (0 _,_ 1 _,_ 0) _,_ (0 _,_ 1 _,_ 1) _,_ (0 _,_ 1 _,_ 2) _,_ (1 _,_ 0 _,_ 0) _}_ 

At the first read operation, we read _E_ 2(0) = 1 at address _dim_ 2(0) = 0: current memory counter is 0. At the second read operation, we read _E_ 2(1) = 1 at address _dim_ 2(1) = 0: current memory counter is 1. And so on... 

**==> picture [449 x 28] intentionally omitted <==**

Following the definition, we fill the write memory with the initial memory state (with zero counters) and the reading results (with incremented counters). 

**==> picture [336 x 12] intentionally omitted <==**

The final memory counter at address 0 equals 3, while at address 1 it equals 1 (check the construction of RS2). One can easy observe that WS2 = RS2 _∪_ S2: 

**==> picture [249 x 26] intentionally omitted <==**

The same logic is applied to the _E_ 1 and _E_ 3 during the CommitSpark walkthrough. 

15 

## **4 Protocol Complexity** 

**Sum-Check Complexity.** Let’s first consider the commitment protocol-agnostic version of the sumcheck instance. During the protocol for an _ℓ_ -variate multilinear polynomial, the prover pre-evaluates each of _ℓ_ polynomials _gj_ with _O_ (2 _[ℓ][−][j]_ ) complexity, and the verifier evaluates _ℓ_ univariate polynomials _gj_ with _O_ (1) complexity. One can observe that _O_ ([�] _[ℓ]_ 1[2] _[ℓ][−][j]_[) =] _[ O]_[(2] _[ℓ]_[).][In the last stage of the protocol, the verifier] evaluates an _ℓ_ -variate multilinear polynomial at a random point corresponding to the one invocation of the evaluate and the verify functions of the commitment protocol. Thus, the total complexity of the algorithm is: 

- Verifier: _O_ ( _ℓ_ + ComVerify) 

- Prover: _O_ (2 _[ℓ]_ + ComEval) 

**Spark complexity.** For the square matrix of size _M × N_ , the Spark protocol complexity then consists 1 of the following parts (here we put _m_ = _N c_ ): 

- Commitment to the polynomials (multiplied by factor _c_ ). Total: _O_ ( _c ·_ Commit); 

- The instance of the sum-check protocol (multiplied by factor _c_ because of a complex input polynomial that depends on _c_ different log _M_ -variate multilinear polynomials _Ei_ ). Total: _O_ ( _cM_ + _c ·_ ComEval) for the prover and _O_ ( _c ·_ log _M_ + _c ·_ ComVerify) for the verifier; 

- The evaluation of WS _i,_ RS _i_ and S _i_ multisets (multiplied by factor _c_ for linear combination to reduce the number of grand-products invocations). Total: _O_ ( _c_ ( _m_ + _M_ )) for prover; 

- The instance of the grand-products protocol (with a complex function – multiplied by factor _c_ ). Complexity is mostly the same as for the sum-check instance. 

|Commit|_O_(_c ·_Commit)|
|---|---|
|Prove|_O_(_c · M_ +_c · m_+_c ·_ComEval)|
|Verify|_O_(_c ·_log_M_ +_c ·_ComVerify)|



## **5 Surge: a Generalization of Spark** 

In Spark we suppose to have an input vector _r ∈_ [ _N_ ] that we represent in a binary form _{_ 0 _,_ 1 _}_[log] _[ N]_ and log _N_ then split into the _c_ smaller chunks receiving ( _r_ 1 _, . . . , rc_ ) _∈_ ( _{_ 0 _,_ 1 _} c_ ) _[c]_ . We also decompose some log _N_ - variate polynomial _t_ into _c_ smaller[lo][g] _c[ N]_ -variate polynomials and pre-compute all possible evaluations of _ti_ at _ri_ . Then we can evaluate a global result as follows 

**==> picture [67 x 29] intentionally omitted <==**

As a final improvement to the Lasso lookup protocol, [STW23] presents **Surge** , which generalizes this approach by leveraging a “decomposable” polynomial _T_ that can be split on _α_ sub-polynomials, where _α_ = _k · c_ for some natural _k_ . In other words, we name _T_ a “table” of size _N_ and decompose this table on 1 _α_ “sub-tables” of size _N c_ , that we can store in both verifier’s and prover’s memory. We also assume the existence of some _α_ -variate multilinear polynomial _g_ such that following holds: for each _r ∈{_ 0 _,_ 1 _}_[log] _[ N]_ log _N_ we write _r_ = ( _r_ 1 _, . . . , rc_ ) _∈_ ( _{_ 0 _,_ 1 _} c_ ) _[c]_ and 

**==> picture [324 x 11] intentionally omitted <==**

**Note that this definition can be turned into the Spark case if we put** _k_ = 1 **and** _g_ =[�] _[c] i_ =1[.] Then, by following the general Lasso equation 

**==> picture [131 x 25] intentionally omitted <==**

where _j_ goes through all columns of _M × N_ matrix, we can represent the left side of this equation as 

**==> picture [301 x 24] intentionally omitted <==**

16 

where nz( _i_ ) denotes a unique column in row _i_ that stores a non-zero value (namely, 1). We suppose that _T_ as well as nz is decomposable as described above, then we turn the previous equation into the following form: 

**==> picture [136 x 25] intentionally omitted <==**

where 

**==> picture [425 x 11] intentionally omitted <==**

CommitSurge(M : _{_ 0 _,_ 1 _}[M][×][N]_ ) 

|1:|Both _P_ and _V_ stores _α_ sub-tables _Ti_ each of size _N_|1<br>_c_ such that|1<br>_c_ such that|for||any _r ∈{_0_,_|1_}_log_N_ the|1_}_log_N_ the|
|---|---|---|---|---|---|---|---|---|
||following holds:||||||||
||_T_[_r_] =_g_(_T_1[_r_1]_, . . . , Tk_[_r_1]_, Tk_+1[_r_2]_, . . . , T_2_k_[_r_2]_, . . . , Tα−k_+1[_rc_]_, . . . , Tα_[_rc_])||||||||
|2:|_P_<br>executes CommitSona and shares the commitments to||_c_|log_m_-variate polynomials|||||
||_dim_1_, . . . , dimc_, where _dimi_ is assumed to provide indexes to the|||sub-tables _T_(_i−_1)_k_+1_. . . Tik_|||||
||to satisfy the Equation (7) and it’s decomposed form.||||||||
|3:|_V_ randomly chooses _r ∈{_0_,_1_}_log_M_ and sends _r_ to _P_.||||||||
|4:|_P_<br>executes<br>CommitSona<br>for<br>_E_1_, . . . , Eα_|and|_read_||~~_t_~~_s_1_, . . . , read_||~~_t_~~_sα_<br>and||
||_final_<br>~~_c_~~_ts_1_, . . . , final_<br>~~_c_~~_tsα_ and shares the commitments with _V_.||||||||
|5:|_P_ opens to _V_ the value _v_ = �<br>_k∈{_0_,_1_}_log_M_ �eq(_r, k_)_· g_(_E_1(_k_)_, . . . , Eα_(_k_))||||||||
|6:|_P_ and _V_ run SumCheckProtocol<br>�<br>_v_, �eq(_r, x_)_· g_(_E_1(_x_)_, . . . , Eα_(_x_))<br>�|||||_// We assume that the_|||
||_instance of sum-check protocol here operates over commitments _||_to _|_Ei _||_instead of the _||_separate_|
||_commitment to the input polynomial_||||||||
|7:|_V_ chooses a random _τ, γ_ and sends them to _P_||||||||
|8:|**for** _i ∈_1_, . . . , α_ **do**||||||||
|9:|_P_ builds WS_i,_RS_i_ and S_i_ multisets.||||||||
|10:|_P_ sends _V_ the evaluations of _Hτ,γ_(WS_i_)_, Hτ,γ_(RS_i_)|and _Hτ,γ_(S_i_)|||||||
|11:|_P_ and _V_ run GrandProductsProtocol<br>�<br>_{hγ_(_a,_|_v, t_)_−τ}_<br>��|(_a,v,t_)_∈_WS_i_, _Hτ,γ_(WS_i_)<br>�||||||
|12:|_P_ and _V_ run GrandProductsProtocol<br>�<br>_{hγ_(_a,_|_v, t_)_−τ}_<br>��|(_a,v,t_)_∈_RS_i_, _Hτ,γ_(RS_i_)<br>�||||||
|13:|_P_ and _V_ run GrandProductsProtocol<br>�<br>_{hγ_(_a,_|_v, t_)_−τ}_<br>��|(_a,v,t_)_∈_S_i_, _Hτ,γ_(S_i_)<br>�||||||
|14:|**if** _Hτ,γ_(WS_i_) =_Hτ,γ_(RS_i_)_· Hτ,γ_(S_i_) **then**||||||||
|15:|_V_ **rejects**||||||||
|16:|**end if**||||||||
|17:|**end for**||||||||



## **References** 

- [Lun+92] Carsten Lund et al. “Algebraic Methods for Interactive Proof Systems”. In: _Journal of the ACM_ 39.4 (Oct. 1992), pp. 859–868. doi: `10.1145/146585.146605` . 

- [Tha17] Justin Thaler. _Sum-Check Protocol_ . `https : / / people . cs . georgetown . edu / jthaler / sumcheck.pdf` . Lecture notes, COSC 544: Probabilistic Proof Systems. 2017. 

- [Wah+18] Riad S. Wahby et al. “Doubly-Efficient zkSNARKs Without Trusted Setup”. In: _Proceedings of the IEEE Symposium on Security and Privacy (S&P)_ . IEEE, 2018. 

- [Set19] Srinath Setty. _Spartan: Efficient and general-purpose zkSNARKs without trusted setup_ . Cryptology ePrint Archive, Paper 2019/550. 2019. url: `https://eprint.iacr.org/2019/550` . 

- [SL20] Srinath Setty and Jonathan Lee. _Quarks: Quadruple-efficient transparent zkSNARKs_ . Cryptology ePrint Archive, Paper 2020/1275. 2020. url: `https://eprint.iacr.org/2020/ 1275.pdf` . 

- [KST22] Abhiram Kothapalli, Srinath Setty, and Ioanna Tzialla. “Nova: Recursive Zero-Knowledge Arguments from Folding Schemes”. In: _Proceedings of the International Cryptology Conference (CRYPTO)_ . Lecture Notes in Computer Science. Springer, 2022. 

17 

- [Tha22] Justin Thaler. “Proofs, Arguments, and Zero-Knowledge”. In: _Foundations and Trends in Privacy and Security_ 4.2–4 (2022), pp. 117–660. 

- [STW23] Srinath Setty, Justin Thaler, and Riad Wahby. _Unlocking the lookup singularity with Lasso_ . Cryptology ePrint Archive, Paper 2023/1216. 2023. url: `https://eprint.iacr.org/2023/ 1216` . 

18