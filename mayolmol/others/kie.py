#Copyright (c) 2007-2010, Roland Memisevic
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#            THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


""" This module contains code for computing Kernel Information Embeddings.
    Kernel Information Embeddings are a family of probabilistic non-parametric 
    dimensionality reduction algorithms.

    Unlike most standard embedding methods (such as LLE, kernel PCA, UKR, 
    Laplacian Eigenmaps and many others) Kernel Information Embeddings come 
    with both forward- and backward mappings. Thus, after computing embeddings 
    with KIE, it is possible to compute low- dimensional codes for new, 
    previously unseen test-data; to produce 'fantasy-data' by projecting 
    latent-space elements into the data-space, or to efficiently project 
    data-cases onto a learned manifold, for example in order to perform 
    de-noising. 

    Embeddings can be computed using the classes Kie (for simple kernel 
    information embeddings) and Cie (for conditional kernel information 
    embeddings). For more information on these, see the references below.

    To instantiate these classes you need to provide data, a kernel bandwidth 
    and a regularization parameter. Each class contains a params-attribute, 
    a cost()- and a grad()-function, which can be passed to any non-linear, 
    unconstrained optimizer for training. A train()-function that performs
    simple gradient descent (not very fast) is provided for convenience. 

    Latent space elements reside in the attribute Z (which, internally, is 
    just a view onto the params-array). To compute the forward-, or backward-
    mapping or to project new cases onto a learned manifold, use the methods 
    forward() and backward() and project(). 

    This module depends on the modules numpy and matplotlib. 

    For more information on Kernel Information Embeddings see:
    2008. Memisevic, R. "Non-linear latent factor models for revealing 
    structure in high-dimensional data". PhD-thesis, University of Toronto. 
    2006. Memisevic, R. (2006). "Kernel information embeddings." In: 
    Proceedings of the 23rd International Conference on Machine learning 
    (ICML 2006). 
"""

from numpy import zeros, ones, sum, dot, diag, newaxis, exp, log, eye, \
                  hstack, vstack, pi, sqrt, array, arange, argmin, argmax, \
                  kron
from pylab import randn

LARGE = 10.**16


def normalizeshape(x):
    if len(x.shape) < 2:
        return x[:,newaxis]
    else:
        return x


def distmatrix(x,y=None):
    """ Compute distance matrix for the points in (columnwise) data-matrices 
        x and y.
    """
    if y is None: y = x
    if len(x.shape)<2:
        x = x[:,newaxis]
    if len(y.shape)<2:
        y = y[:,newaxis]
    x2 = sum(x**2,0)
    y2 = sum(y**2,0)
    return x2[:,newaxis] + y2[newaxis,:] - 2*dot(x.T,y)


def logsumexp(x,dim=0):
    """Compute log(sum(exp(x))) in numerically stable way."""
    if dim==0:
        xmax = x.max(0)
        return xmax + log(exp(x-xmax).sum(0))
    elif dim==1:
        xmax = x.max(1)
        return xmax + log(exp(x-xmax[:,newaxis]).sum(1))
    else: 
        raise 'dim ' + str(dim) + 'not supported'


def dens1d(data1, data2, h):
    d1_ = (data1**2).sum(0)[newaxis,:]
    d2_ = (data2**2).sum(0)[newaxis,:]
    D = d1_.T + d2_ - 2*dot(data1.T,data2)
    normalizer = 1./(sqrt(pi*h)*data2.shape[1])
    return exp(-D/h).sum(1)*normalizer


def dens2d(data, h, numvals):
    """ Return the 2d-kernel density estimate evaluated on a grid, using data
        as the training data and h as the bandwidths. numvals determines how 
        fine the grid is. 
        
        Returns also the values of the grid which is useful for contour plots.

        Only for 2d-data. 
    """
    dens = []
    span0 = (data[0].max()-data[0].min())
    span1 = (data[1].max()-data[1].min())
    xrange = arange(data[0].min()-span0/5.,
                        data[0].max()+span0/5., span0/numvals)
    yrange = arange(data[1].min()-span1/5.,
                        data[1].max()+span1/5., span1/numvals)
    testdata = vstack((kron(ones((1,len(yrange))),xrange[newaxis,:]),
                       kron(yrange[newaxis,:],ones((1,len(xrange))))))
    d1_ = (testdata**2).sum(0)[newaxis,:]
    d2_ = (data**2).sum(0)[newaxis,:]
    D = d1_.T + d2_ - 2*dot(testdata.T,data)
    normalizer = 1./(pi*h*data.shape[1])
    density = exp(-D/h).sum(1)*normalizer
    count = 0
    for x in xrange:
        for y in yrange:
            dens.append(density[count])
            count += 1
    
    dens = array(dens).reshape(xrange.shape[0], yrange.shape[0]).T
    return xrange, yrange, dens


def optbandwidth(data, hmin, hmax, numsteps):
    numdims, numcases = data.shape
    #bandwidths = arange(data.var()/10, 10*data.var(), data.var())
    bandwidths = arange(hmin, hmax, (hmax-hmin)/numsteps)
    gram = dot(data.T, data)
    D = diag(gram)[:,newaxis] + diag(gram)[newaxis,:] - 2 * gram
    E = eye(numcases)*LARGE
    dens = []
    lognumcases = log(numcases)
    for h in bandwidths:
        lognormalizer = lognumcases+0.5*numdims*log(pi*h)
        dens.append(logsumexp(-(D/h+E),1).sum()/numcases - lognormalizer)
        print "bandwidth: %f : log-density %f" % (h, dens[-1])
    print "best: %f at %d of %d" % (bandwidths[argmax(dens)], argmax(dens)+1, len(bandwidths))
    return bandwidths[argmax(dens)], dens


def contourlat(model, numvals):
    """ Return the data for countour-plot of the latent density.
        Only for 2d-latent spaces. 
    """
    dens = []
    span0 = (model.Z[0].max()-model.Z[0].min())
    span1 = (model.Z[1].max()-model.Z[1].min())
    xrange = arange(model.Z[0].min()-span0/5.,
                        model.Z[0].max()+span0/5., span0/numvals)
    yrange = arange(model.Z[1].min()-span1/5.,
                        model.Z[1].max()+span1/5., span1/numvals)
    for x in xrange:
        for y in yrange:
            dens.append(model.latdensity(hstack((x,y))))
    
    dens = array(dens).reshape(xrange.shape[0], yrange.shape[0]).T
    return xrange, yrange, dens


def contourobs(model, numvals):
    """ Return the data for countour-plot of the observable space density.
        Only for 2d-latent spaces. 
    """
    dens = []
    span0 = (model.Z[0].max()-model.Z[0].min())
    span1 = (model.Z[1].max()-model.Z[1].min())
    xrange = arange(model.Z[0].min()-span0/5.,
                        model.Z[0].max()+span0/5., span0/numvals)
    yrange = arange(model.Z[1].min()-span1/5.,
                        model.Z[1].max()+span1/5., span1/numvals)
    for x in xrange:
        for y in yrange:
            dens.append(model.obsdensity(model.forward(hstack((x,y)))))
    
    dens = array(dens).reshape(xrange.shape[0], yrange.shape[0]).T
    return xrange, yrange, dens


def gaussKernelMatrix(Z, h):
    GRAMZ = dot(Z.T,Z)
    return exp(-(1.0/h)*
             (diag(GRAMZ)[newaxis,:] + diag(GRAMZ)[:,newaxis] - 2 * GRAMZ))


def classKernelMatrix(Z):
    """Return the Grammian for the 'one-hot'-encoded class-label matrix."""
    return dot(Z.T,Z)


def penfunc_squarednorm(Z):
    return sum(sum(Z**2))


def pengrad_squarednorm(Z):
    return 2*Z


class Kie(object):
    """ Kernel information embedding. 
    
    Compute a low-dimensional embedding of data by maximizing an estimate 
    of the mutual information between the embedding and the original data.
    Data is denoted Y and the embedding is denoted Z. 
    """

    def __init__(self, q, hy, Y, reg, loo, learnbandwidth=False, 
                                           penfunc=penfunc_squarednorm, 
                                           pengrad=pengrad_squarednorm):
        self.loo = loo   #use leave-one-out-estimate?
        self.learnbandwidth = learnbandwidth  #optimize bandwidth, too?
        self.q = q
        self.Y = Y
        self.penfunc = penfunc
        self.pengrad = pengrad
        self.loghy = array(log(hy))
        self.d, self.numcases = Y.shape
        self.lognumcases = log(self.numcases)
        self.reg = reg     #amount of regularization
        self.Z = randn(self.q,self.numcases) * 0.1
        #some quantities useful for gradient/cost computation:
        GRAMY = dot(Y.T,Y)
        self.YY = diag(GRAMY)[newaxis,:] + diag(GRAMY)[:,newaxis] - 2 * GRAMY
        self.kY = -(1.0/exp(self.loghy)) * self.YY
        if self.loo: 
            self.kY -= eye(self.numcases)*LARGE
        self.KY = exp(self.kY)  #kernel matrix
        if not self.learnbandwidth:
            self.params = self.Z.reshape(self.q*self.numcases)
        else:
            self.params = hstack((self.Z.reshape(self.q*self.numcases), self.loghy))
            self.Z = self.params[:-1].reshape(self.q,self.numcases)
            self.loghy = self.params[-1:]

    def updateloghy(self,loghy):
        self.loghy = loghy
        self.kY = -(1.0/exp(self.loghy)) * self.YY
        if self.loo: 
            self.kY -= eye(self.numcases)*LARGE
        self.KY = exp(self.kY) 
 
    def cost(self):
        GRAMZ = dot(self.Z.T,self.Z)
        kZ = - (diag(GRAMZ)[newaxis,:] + diag(GRAMZ)[:,newaxis] - 2 * GRAMZ)
        if self.learnbandwidth:
            self.kY = -(1.0/exp(self.loghy)) * self.YY
            if self.loo: 
                self.kY -= eye(self.numcases)*LARGE
            self.KY = exp(self.kY)
        if self.loo:
            kZ -= eye(self.numcases)*LARGE
        cost = - sum(logsumexp(self.kY+kZ,1))/self.numcases \
               + sum(logsumexp(kZ,1))/self.numcases
        if self.learnbandwidth:
            cost += self.lognumcases + 0.5*self.d*log(pi*exp(self.loghy))
            cost = cost[0]
        #add penalty:
        cost += (self.reg/self.numcases) * self.penfunc(self.Z)
        return cost
    
    def grad(self):
        GRAMZ = dot(self.Z.T,self.Z)
        KZ = exp(-(diag(GRAMZ)[newaxis,:] + diag(GRAMZ)[:,newaxis] - 2*GRAMZ))
        if self.learnbandwidth:
            self.kY = -(1.0/exp(self.loghy)) * self.YY
            if self.loo: 
                self.kY -= eye(self.numcases)*LARGE
            self.KY = exp(self.kY)
        if self.loo:
            KZ *= (1.-eye(self.numcases))
        sumKZ = sum(KZ,1)
        oneoversumKZ = 1./sumKZ
        sumKZKY = sum(KZ*self.KY,1)
        gradZ = zeros((self.q, self.numcases), dtype=float)
        for l in range(self.numcases):
            gradZ[:, l] = \
                sum(((self.Z[:,l][:,newaxis] - self.Z)
                      *KZ[l,:][newaxis,:]
                      *( (self.KY[l,:]/sumKZKY[l])[:,newaxis]
                        +(self.KY[l,:]/sumKZKY.T)[:,newaxis]
                        -oneoversumKZ[l]
                        -oneoversumKZ.T[:,newaxis]
                       ).T),1)
        gradZ *= 2.0 / self.numcases
        gradZ += (self.reg/self.numcases) * self.pengrad(self.Z)
        if not self.learnbandwidth:
            return gradZ.flatten()
        else:
            Dh = -sum(sum(((KZ*self.KY)/sumKZKY[:,newaxis])*self.YY,1),0) \
                 / (self.numcases*exp(self.loghy)) \
                 + (0.5*self.d)
            return hstack((gradZ.flatten(),Dh))

    def f(self,params):
        """Wrapper function around cost function to check grads, etc."""
        paramsold = self.params.copy()
        self.updateparams(params.copy().flatten())
        result = self.cost() 
        self.updateparams(paramsold.copy())
        return result

    def g(self,params):
        """Wrapper function around gradient to check grads, etc."""
        paramsold = self.params.copy()
        self.updateparams(params.copy().flatten())
        result = self.grad()
        self.updateparams(paramsold.copy())
        return result

    def updateparams(self,newparams):
        self.params *= 0.0
        self.params += newparams.copy()

    def forward(self, Ztest):
        Ztest = normalizeshape(Ztest)
        kz = -distmatrix(Ztest, self.Z)
        lse = logsumexp(kz, 1)[:,newaxis]
        return sum(exp(kz-lse)[:,:,newaxis]* 
                    self.Y[:,:,newaxis].transpose(2, 1, 0), 1).T

    def backward(self, Ytest):
        Ytest = normalizeshape(Ytest)
        ky = -(1.0/exp(self.loghy))*distmatrix(Ytest, self.Y)
        lse = logsumexp(ky, 1)[:,newaxis]
        return sum(exp(ky-lse)[:,:,newaxis]* 
                    self.Z[:,:,newaxis].transpose(2, 1, 0), 1).T

    def project(self, y):
        return self.forward(self.backward(y))

    def latdensity(self,z):
        return sum(exp(-sum((z[:,newaxis]-self.Z)**2,0))) / self.Znormalize

    def obsdensity(self,y):
        return sum(exp(-sum((y[:,newaxis]-self.Y)**2,0) / exp(self.loghy))) \
               / self.Ynormalize

    def train(self, numsteps, verbose=True, stepsize=[0.001]):
        for s in range(numsteps):
            if stepsize[0] < 10**-10: 
                print "stepsize < 10**-10: exiting" 
                return
            if s == 0:
                oldcost = self.cost()
                if verbose:
                    print "initial cost: %f " % oldcost
            g = self.grad()
            self.params -= stepsize[0] * g
            newcost = self.cost()
            if newcost <= oldcost:
                if verbose:
                    print "cost: %f " % newcost
                    print "increasing step-size to %f" % stepsize[0]
                oldcost = newcost
                stepsize[0] = stepsize[0] * 1.1
            else:
                if verbose:
                    print "cost: %f larger than best cost %f" % \
                                                            (newcost, oldcost)
                    print "decreasing step-size to %f" % stepsize[0]
                self.params += stepsize[0] * g
                newcost = oldcost
                stepsize[0] *= 0.5



class Cie(object):
    """ Conditional kernel information embedding.
    
    Compute a conditional embedding of data by factoring out known 
    information. 
    """
    def __init__(self, q, KX=None, X=None, hx=None, 
                          KY=None, Y=None, hy=None, reg=0.1):
        self.q = q
        self.d, self.numcases = Y.shape
        self.reg = reg     #amount of regularization
        self.Z = randn(self.q, self.numcases)*0.1
        self.Y = Y
        #some quantities useful for gradient/cost computation:
        if Y == None:
            self.KY = KY
        else:
            self.hy = hy
            self.KY = gaussKernelMatrix(Y, hy)
        if X == None:
            self.KX = KX
        else:
            self.hx = hx
            self.KX = gaussKernelMatrix(X, hx)
            self.X = X
        self.params = self.Z.reshape(self.q*self.numcases)

    def cost(self):
        #NOTE: H(Z) = -(MINUS!) logsum...
        KZ = gaussKernelMatrix(self.Z, 1.0)
        sumKZKX = sum(KZ*self.KX,1)
        sumKZKXKY = sum(KZ*self.KX*self.KY,1)
        cost = -sum( - log(sumKZKX) + log(sumKZKXKY) ) / self.numcases
        #add penalty:
        cost += (self.reg/self.numcases) * sum(sum(self.Z*self.Z))
        return cost

    def grad(self):
        #----this is redundant and could be avoided if cost/grad were together:
        KZ = gaussKernelMatrix(self.Z, 1.0)
        sumKZKX = sum(KZ*self.KX,1)
        sumKZKXKY = sum(KZ*self.KX*self.KY,1)
        #----------
        grad = zeros((self.q, self.numcases), dtype=float)
        KXoversumKZKX = self.KX/sumKZKX[newaxis,:]
        KXoversumKZKX_ = self.KX/sumKZKX[:,newaxis]
        KYKX = self.KY*self.KX
        KYKXoversumKZKXKY = KYKX/sumKZKXKY[newaxis,:]
        KYKXoversumKZKXKY_ = KYKX/sumKZKXKY[:,newaxis]
        for l in range(self.numcases):
            grad[:, l] += \
                -sum((self.Z[:,l][:,newaxis] - self.Z)*KZ[l, :][newaxis,:]*
                                (KXoversumKZKX_[l,:]
                                 +KXoversumKZKX[l,:]
                                 -KYKXoversumKZKXKY_[l,:]
                                 -KYKXoversumKZKXKY[l,:])[newaxis,:]
                    , 1)
        grad *= (2.0/self.numcases)
        #add penalty-gradient:
        grad = grad + 2 * (self.reg/self.numcases) * self.Z
        return grad.flatten()

    def f(self,params):
        """Wrapper function around cost function to check grads, etc."""
        paramsold = self.params.copy()
        self.updateparams(params.copy().flatten())
        result = self.cost() 
        self.updateparams(paramsold.copy())
        return result

    def g(self,params):
        """Wrapper function around gradient to check grads, etc."""
        paramsold = self.params.copy()
        self.updateparams(params.copy().flatten())
        result = self.grad()
        self.updateparams(paramsold.copy())
        return result

    def updateparams(self,newparams):
        self.params *= 0.0
        self.params += newparams.copy()

    def forward(self, Ztest):
        Ztest = normalizeshape(Ztest)
        #kz = -sum((z[:,newaxis]-self.Z)**2, 0)
        #lse = logsumexp(kz)
        #return sum(exp(kz-lse)[newaxis,:]*self.Y,1)
        kz = -distmatrix(Ztest, self.Z)
        lse = logsumexp(kz, 1)[:,newaxis]
        return sum(exp(kz-lse)[:,:,newaxis]* 
                    self.Y[:,:,newaxis].transpose(2, 1, 0), 1).T

    def backward(self, Ytest):
        Ytest = normalizeshape(Ytest)
        #ky = -(1.0/self.hy)*sum((y[:,newaxis]-self.Y)**2, 0)
        #lse = logsumexp(ky)
        #return sum(exp(ky-lse)[newaxis,:]*self.Z,1)
        ky = -(1.0/exp(self.loghy))*distmatrix(Ytest, self.Y)
        lse = logsumexp(ky, 1)[:,newaxis]
        return sum(exp(ky-lse)[:,:,newaxis]* 
                    self.Z[:,:,newaxis].transpose(2, 1, 0), 1).T

    def forwardxz(self, x, z):
        kz = -sum((z[:,newaxis]-self.Z)**2, 0)
        kx = -sum((x[:,newaxis]-self.X)**2, 0)
        k = kz + kx
        lse = logsumexp(k)
        return sum(exp(k-lse)[newaxis,:]*self.Y,1)

    def project(self, y):
        return self.forward(self.backward(y))

    def train(self, numsteps, verbose=True, stepsize=[0.001]):
        for s in range(numsteps):
            if stepsize[0] < 10**-10: 
                print "stepsize < 10**-10: exiting" 
                return
            if s == 0:
                oldcost = self.cost()
                if verbose:
                    print "initial cost: %f " % oldcost
            g = self.grad()
            self.params -= stepsize[0] * g
            newcost = self.cost()
            if newcost <= oldcost:
                if verbose:
                    print "cost: %f " % newcost
                    print "increasing step-size to %f" % stepsize[0]
                oldcost = newcost
                stepsize[0] = stepsize[0] * 1.1
            else:
                if verbose:
                    print "cost: %f larger than best cost %f" % \
                                                            (newcost, oldcost)
                    print "decreasing step-size to %f" % stepsize[0]
                self.params += stepsize[0] * g
                newcost = oldcost
                stepsize[0] *= 0.5

