from pathlib import Path
import re,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
text=(HERE/'before/references.bib').read_text(encoding='utf-8')
def setfield(block,field,value):
    pattern=rf'^  {field}\s*=.*$'
    line=f'  {field} = {{{value}}},'
    if re.search(pattern,block,re.M): return re.sub(pattern,lambda _:line,block,flags=re.M)
    prefix=block.rstrip().removesuffix('}').rstrip()
    if not prefix.endswith(','): prefix+=','
    return prefix+'\n'+line+'\n}\n\n'

# Publication metadata is updated only where the verified record adds a
# missing field or corrects the confirmed Huang page range. No bulk overwrite.
updates=['cai2026','shen2025','li2023','ying2026','mei2022','ke2020']
blocks=re.split(r'(?=^@)',text,flags=re.M)
for i,b in enumerate(blocks):
    key=re.search(r'^@\w+\{([^,]+),',b)
    if not key: continue
    k=key[1]
    if k in updates:
        meta=json.loads((HERE/'metadata'/f'{k}.json').read_text(encoding='utf-8'))
        for src,dst in [('volume','volume'),('issue','number'),('page','pages')]:
            if meta.get(src): b=setfield(b,dst,meta[src].replace('-','--') if src=='page' else meta[src])
    if k=='huang2026': b=setfield(b,'pages','2949--2953')
    if k in ['zhu1997','TroppGilbertStrauss2006SOMP','vila2013']:
        meta=json.loads((HERE/'metadata'/f'{k}.json').read_text(encoding='utf-8'))
        b=setfield(b,'doi',meta['DOI'])
    if k=='ding2026':
        b=setfield(b,'note',r'Early access, doi: 10.1109/TVT.2026.3729877')
    # Preserve provenance in BibTeX metadata while avoiding redundant links
    # for published articles or proceedings identifiable from the citation.
    if b.startswith('@article') or b.startswith('@inproceedings'):
        b=re.sub(r'^  url =', '  source_url =',b,flags=re.M)
    if k in ['xu2019otfs','dytso2021','metzler2014','wei2026','shastri2022']:
        b=re.sub(r'^  url =', '  source_url =',b,flags=re.M)
    if k=='shastri2022': b=setfield(b,'howpublished','arXiv:2206.05049v2')
    blocks[i]=b
text=''.join(blocks)
abbr={
 'IEEE Transactions on Wireless Communications':'IEEE Trans. Wireless Commun.',
 'IEEE Transactions on Signal Processing':'IEEE Trans. Signal Process.',
 'IEEE Transactions on Vehicular Technology':'IEEE Trans. Veh. Technol.',
 'IEEE Transactions on Communications':'IEEE Trans. Commun.',
 'IEEE Transactions on Information Theory':'IEEE Trans. Inf. Theory',
 'IEEE Journal on Selected Areas in Communications':'IEEE J. Sel. Areas Commun.',
 'IEEE Wireless Communications Letters':'IEEE Wireless Commun. Lett.',
 'IEEE Signal Processing Letters':'IEEE Signal Process. Lett.',
 'Journal of Machine Learning Research':'J. Mach. Learn. Res.',
 'Journal of the American Statistical Association':'J. Amer. Stat. Assoc.',
 'Neural Computation':'Neural Comput.',
 'Computational Optimization and Applications':'Comput. Optim. Appl.',
 'ACM Transactions on Mathematical Software':'ACM Trans. Math. Softw.',
 'Signal Processing':'Signal Process.',
 'Advances in Neural Information Processing Systems':'Adv. Neural Inf. Process. Syst.',
 'Proc. IEEE Wireless Communications and Networking Conference (WCNC)':'Proc. IEEE Wireless Commun. Netw. Conf. (WCNC)',
 'Proceedings of the Seventeenth Conference on Uncertainty in Artificial Intelligence':'Proc. Conf. Uncertainty Artif. Intell. (UAI)',
 'Proceedings of the 33rd International Conference on Machine Learning':'Proc. Int. Conf. Mach. Learn. (ICML)',
}
for old,new in abbr.items(): text=text.replace('= {'+old+'}', '= {'+new+'}')
text += r'''
@article{kodheli2021,
  author = {Oltjon Kodheli and Eva Lagunas and Nicola Maturo and Shree Krishna Sharma and Bhavani Shankar and Jesus Fabian Mendoza Montoya and Juan Carlos Merlano Duncan and Danilo Spano and Symeon Chatzinotas and Steven Kisseleff and Jorge Querol and Lei Lei and Thang X. Vu and George Goussetis},
  title = {Satellite communications in the new space era: A survey and future challenges},
  journal = {IEEE Commun. Surveys Tuts.},
  volume = {23},
  number = {1},
  pages = {70--109},
  year = {2021},
  doi = {10.1109/COMST.2020.3028247},
  source_url = {https://arxiv.org/abs/2002.08811},
}

@article{ma2017,
  author = {Junjie Ma and Li Ping},
  title = {Orthogonal {AMP}},
  journal = {IEEE Access},
  volume = {5},
  pages = {2020--2033},
  year = {2017},
  doi = {10.1109/ACCESS.2017.2653119},
  source_url = {https://arxiv.org/abs/1602.06509},
}

@article{rangan2019,
  author = {Sundeep Rangan and Philip Schniter and Alyson K. Fletcher},
  title = {Vector approximate message passing},
  journal = {IEEE Trans. Inf. Theory},
  volume = {65},
  number = {10},
  pages = {6664--6684},
  year = {2019},
  doi = {10.1109/TIT.2019.2916359},
  source_url = {https://arxiv.org/abs/1610.03082},
}

@article{hyvarinen2005,
  author = {Aapo Hyv{\"a}rinen},
  title = {Estimation of non-normalized statistical models by score matching},
  journal = {J. Mach. Learn. Res.},
  volume = {6},
  pages = {695--709},
  year = {2005},
  source_url = {https://www.jmlr.org/papers/v6/hyvarinen05a.html},
}

@article{wax1985,
  author = {Mati Wax and Thomas Kailath},
  title = {Detection of signals by information theoretic criteria},
  journal = {IEEE Trans. Acoust., Speech, Signal Process.},
  volume = {33},
  number = {2},
  pages = {387--392},
  year = {1985},
  doi = {10.1109/TASSP.1985.1164557},
}

@inproceedings{lin2017,
  author = {Guosheng Lin and Anton Milan and Chunhua Shen and Ian Reid},
  title = {{RefineNet}: Multi-path refinement networks for high-resolution semantic segmentation},
  booktitle = {Proc. IEEE Conf. Comput. Vis. Pattern Recognit. (CVPR)},
  pages = {5168--5177},
  year = {2017},
  doi = {10.1109/CVPR.2017.549},
  source_url = {https://openaccess.thecvf.com/content_cvpr_2017/html/Lin_RefineNet_Multi-Path_Refinement_CVPR_2017_paper.html},
}

@IEEEtranBSTCTL{IEEEcontrol,
  CTLuse_forced_etal = {yes},
  CTLmax_names_forced_etal = {6},
  CTLnames_show_etal = {1},
}
'''
text=text.replace('% References for the manuscript and its 14-paper writing corpus.','% References and verified publication metadata for the manuscript.\n% source_url retains provenance without printing redundant online links.\n% IEEEcontrol applies first-author et al. to references with more than six authors.')
(ROOT/'references.bib').write_text(text,encoding='utf-8')
main=(ROOT/'main.tex').read_text(encoding='utf-8')
assert '\\bstctlcite' not in main
main=main.replace('\\begin{document}', '\\begin{document}\n\\bstctlcite{IEEEcontrol}')
(ROOT/'main.tex').write_text(main,encoding='utf-8')
print('Bibliography revised; six new records plus two previously uncited records will yield 43 references.')
