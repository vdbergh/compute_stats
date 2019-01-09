from __future__ import division
import sys,os.path,math,random
import scipy.stats as stats_
import numpy
import sys,os.path
import chess
import chess.pgn

def create_digest(test):
    pgn_file=test+".pgn"
    if not os.path.exists(pgn_file):
        return False
    digest_file=test+".digest"
    if os.path.exists(digest_file):
        return False
    print("Creating %s" % digest_file)
    pgn = open(pgn_file)
    n=0
    games={}
    game=None
    digest=open(digest_file,"w")
    first_white=None
    while True:
        header=chess.pgn.read_headers(pgn)
        if not header:
            break
        n+=1
        if n%100==0:
            sys.stdout.write("%d,%d            \r" % (n,len(games.keys())))
            sys.stdout.flush()
        fen=header.get('FEN')
        if not fen: # 8 book test
            break
        result=header['Result']
        white=header['White']
        if not first_white:
            first_white=white
        if fen in games.keys():
            result_last,white_last=games[fen]
            if result!="*" and result_last!="*" and white!=white_last:
                if white==first_white:
                    digest.write(fen+" "+result+" "+result_last+"\n")
                else:
                    digest.write(fen+" "+result_last+" "+result+"\n")
                del games[fen]
        else:
            games[fen]=(result,white)
    digest.close()
    pgn.close()
    return True

def to_score(result):
    if result=="1-0":
        return 2
    elif result=="1/2-1/2":
        return 1
    elif result=="0-1":
        return 0

def score_to_elo(s):
    return -400*math.log(1/s-1)/math.log(10)

def elo_to_score(e):
    return 1/(1+10**(-e/400))

def fe(a,b):
    epsilon=1e-6
    return abs(a-b)<epsilon

class compute:

    def __init__(self,test,randomize=False):
        self.calc=[]
        self.stats={}
        self.test=test
        self.randomize=randomize
        ret=self.assemble()
        if not ret:
            return
        self.marginals()
        self.chi2()
        self.trinomial()
        self.pentanomial()
        self.ldw()
        self.scores()
        self.elos()
        self.variances()
        self.correlation()
        self.variance_pentanomial()

    def assemble(self):
        self.calc.extend(['name','all'])
        digest_file=test+".digest"
        if not os.path.exists(digest_file) and not create_digest(test):
            return
        self.stats['name']=test
        digest=open(digest_file,"r")
        lines=digest.readlines()
        collect1=[]
        collect2=[]
        for l in lines:
            l=l.split()
            result1=l[-2]
            result2=l[-1]
            collect1.append(result1)
            collect2.append(result2)
        if self.randomize:
            random.shuffle(collect1)
            random.shuffle(collect2)
        self.stats['all']={}
        for i in range(0,3):
            for j in range(0,3):
                self.stats['all'][(i,j)]=0
        if len(collect1)==0:
            return False
        for u in range(0,len(collect1)):
            result1=collect1[u]
            result2=collect2[u]
            score1=to_score(result1)
            score2=to_score(result2)
            self.stats['all'][(score1,2-score2)]+=1
        return True

    def marginals(self):
        self.calc.extend(['white','black','N2'])
        self.stats['white']=3*[0]
        self.stats['black']=3*[0]
        self.stats['N2']=0
        for i in range(0,3):
            for j in range(0,3):
                s=self.stats['all'][(i,j)]
                self.stats['white'][i]+=s
                self.stats['black'][j]+=s
                self.stats['N2']+=s
        assert(sum(self.stats['white'])==self.stats['N2'])
        assert(sum(self.stats['black'])==self.stats['N2'])
        assert(sum(self.stats['all'].values())==self.stats['N2'])

    def chi2(self):
        self.calc.extend(['chi2','p_chi2'])
        self.stats['chi2']=0
        e_s=0
        for i in range(0,3):
            for j in range(0,3):
                e=(self.stats['white'][i]*self.stats['black'][j])/self.stats['N2']
                e_s+=e
                o=self.stats['all'][(i,j)]
                if e<5:
                    del self.stats['chi2']
                    return
                self.stats['chi2']+=(e-o)**2/e
        self.stats['p_chi2']=1-stats_.chi2.cdf(self.stats['chi2'],(3-1)*(3-1))
        assert(fe(e_s,self.stats['N2']))

    def trinomial(self):
        self.calc.append('trinomial')
        self.stats['trinomial']=3*[0]
        for i in range(0,3):
            self.stats['trinomial'][i]=self.stats['white'][i]+self.stats['black'][i]
        assert(sum(self.stats['trinomial'])==2*self.stats['N2'])

    def pentanomial(self):
        self.calc.append('pentanomial')
        self.stats['pentanomial']=5*[0]
        for i in range(0,3):
            for j in range(0,3):
                self.stats['pentanomial'][i+j]+=self.stats['all'][(i,j)]
        assert(sum(self.stats['pentanomial'])==self.stats['N2'])

    def ldw(self):
        self.calc.extend(['ldw','ldw_white','ldw_black','ldw_pentanomial'])
        self.stats['ldw']=3*[0]
        self.stats['ldw_white']=3*[0]
        self.stats['ldw_black']=3*[0]
        self.stats['ldw_pentanomial']=5*[0]
        for i in range(0,3):
            self.stats['ldw'][i]=self.stats['trinomial'][i]/(2*self.stats['N2'])
            self.stats['ldw_white'][i]=self.stats['white'][i]/self.stats['N2']
            self.stats['ldw_black'][i]=self.stats['black'][i]/self.stats['N2']
        for i in range(0,5):
            self.stats['ldw_pentanomial'][i]=self.stats['pentanomial'][i]/self.stats['N2']
        assert(fe(sum(self.stats['ldw']),1))
        assert(fe(sum(self.stats['ldw_white']),1))
        assert(fe(sum(self.stats['ldw_black']),1))
        assert(fe(sum(self.stats['ldw_pentanomial']),1))

    def scores(self):
        self.calc.extend(['score','score_white','score_black'])
        self.stats['score']=self.stats['ldw'][2]+self.stats['ldw'][1]/2
        self.stats['score_white']=self.stats['ldw_white'][2]+self.stats['ldw_white'][1]/2
        self.stats['score_black']=self.stats['ldw_black'][2]+self.stats['ldw_black'][1]/2
        assert(fe(self.stats['score'],(self.stats['score_white']+self.stats['score_black'])/2))

    def elos(self):
        self.calc.extend(['elo','elo_white','elo_black'])
        self.stats['elo']=score_to_elo(self.stats['score'])
        self.stats['elo_white']=score_to_elo(self.stats['score_white'])
        self.stats['elo_black']=score_to_elo(self.stats['score_black'])
        assert(fe(elo_to_score(self.stats['elo']),self.stats['score']))
        assert(fe(elo_to_score(self.stats['elo_white']),self.stats['score_white']))
        assert(fe(elo_to_score(self.stats['elo_black']),self.stats['score_black']))

    def variances(self):
        self.calc.extend(['variance','variance_white','variance_black'])
        self.stats['variance']=(self.stats['ldw'][2]+self.stats['ldw'][1]/4-self.stats['score']**2)
        self.stats['variance_white']=(self.stats['ldw_white'][2]+self.stats['ldw_white'][1]/4-self.stats['score_white']**2)
        self.stats['variance_black']=(self.stats['ldw_black'][2]+self.stats['ldw_black'][1]/4-self.stats['score_black']**2)
        variance_alt=(self.stats['variance_white']+self.stats['variance_black'])/2+(self.stats['score_white']-self.stats['score_black'])**2/4
        assert(fe(self.stats['variance'],variance_alt))

    def correlation(self):
        self.calc.extend(['covariance','correlation','p_correlation'])
        m2=0
        for i in range(0,3):
            for j in range(0,3):
                m2+=(i/2)*(j/2)*self.stats['all'][(i,j)]/self.stats['N2']
        self.stats['covariance']=m2-self.stats['score_white']*self.stats['score_black']
        try:
            self.stats['correlation']=self.stats['covariance']/(self.stats['variance_white']*self.stats['variance_black'])**.5
        except ZeroDivisionError:
            return
    # t-transformation
        if self.stats['N2']>=2:
            c=self.stats['correlation']
            N2=self.stats['N2']
            t=c*((N2-2)/(1-c*c))**.5
            self.stats['p_correlation']=2*(1-stats_.t.cdf(abs(t),N2-2))
    # fisher transformation
        if self.stats['N2']>3:
            z=numpy.arctanh(self.stats['correlation'])*(self.stats['N2']-3)**.5
            self.stats['p_correlation2']=2*(1-stats_.norm.cdf(abs(z)))

    def variance_pentanomial(self):
        self.calc.extend(['variance_pentanomial','variance_ratio'])
        m2=0
        m1=0
        for i in range(0,5):
            m2+=self.stats['ldw_pentanomial'][i]*(i/2)*(i/2)
            m1+=self.stats['ldw_pentanomial'][i]*(i/2)
        self.stats['variance_pentanomial']=(m2-(2*self.stats['score'])**2)/2
        try:
            self.stats['variance_ratio']=self.stats['variance_pentanomial']/self.stats['variance']
        except ZeroDivisionError:
            pass
        if self.stats.get('covariance')!=None:
            variance_alt=(self.stats['variance_white']+self.stats['variance_black']+2*self.stats['covariance'])/2
            assert(fe(self.stats['variance_pentanomial'],variance_alt))

    def __str__(self):
        s=''
        for k in self.calc:
            v=self.stats.get(k)
            if v!=None:
                s+="%s=%s\n" % (k,repr(v))
        return s


if __name__=='__main__':
    work=[]
    for l in sys.argv[1:]:
        test=l.split(".")[0]
        work.append(test)
        work=list(set(work))
    for test in work:
        c=compute(test,randomize=False)
        if os.path.exists(test+".pgn"):
            stats_file=test+".stats"
            f=open(stats_file,"w")
            print("Writing %s" % stats_file)
            f.write(str(c))
            f.close()
