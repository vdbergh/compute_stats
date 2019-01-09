# compute_stats
A script which computes various statistical characteristics of a pgn file. 

This script was specifically written to process pgn files written for the [fishtest](http://tests.stockfishchess.org/tests) framework. It assumes that every game has a `Setup` tag and moreover that every game is paired with one with reversed colors (however such paired games do not have to be consecutive in the pgn file). Games that do not satisfy these conditions are discarded.

Usage is very simple:  
```
python3 compute_stats.py <pgn list>
```
For every element of `<pgn list>` a corresponding file will be written with the extension `.stats`. The `.stats` files are actually python files which can, for example, be loaded with execfile. Here is an example of a .stats file.
```
name='5beda64e0ebc595e0ae3827f'
all={(0, 1): 294, (1, 2): 281, (0, 0): 65, (2, 0): 189, (1, 0): 481, (2, 2): 59, (0, 2): 87, (2, 1): 459, (1, 1): 1670}
white=[446, 2432, 707]
black=[735, 2423, 427]
N2=3585
chi2=52.411896304248685
p_chi2=1.1312673020569264e-10
trinomial=[1181, 4855, 1134]
pentanomial=[65, 775, 1946, 740, 59]
ldw=[0.16471408647140864, 0.6771269177126917, 0.1581589958158996]
ldw_white=[0.12440725244072524, 0.6783821478382148, 0.19721059972105998]
ldw_black=[0.20502092050209206, 0.6758716875871688, 0.11910739191073919]
ldw_pentanomial=[0.01813110181311018, 0.21617852161785217, 0.5428172942817294, 0.20641562064156208, 0.016457461645746164]
score=0.49672245467224546
score_white=0.5364016736401673
score_black=0.4570432357043236
elo=-2.277504381281642
elo_white=25.33930591615504
elo_black=-29.923184934314456
variance=0.08070752826845157
variance_white=0.0790793811966411
variance_black=0.07918679450445348
covariance=-0.009036022945443312
correlation=-0.11418769660022109
p_correlation=7.030820370346191e-12
variance_pentanomial=0.07009706490510403
variance_ratio=0.8685319251996577
```
Some precomputed `.stats` files are in the `results` directory. They correspond to tests on the fishtest framework. The actual pgn files can be found at https://drive.google.com/drive/folders/1fR2gmzKpxjomb4GhyOLcNDFCodzSXq-O. Metadata about the corresponding tests can be found at http://tests.stockfishchess.org/tests/view/ `<test-id>` and http://tests.stockfishchess.org/api/get_run/ `<test-id>` where `<test-id>` is the name of the `.stats` file without the extension.
