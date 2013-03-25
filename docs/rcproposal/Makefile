
lyx_files=rc_proposal.lyx

.PHONY: all

all:: rc_proposal.pdf


rc_proposal.lyx: 
	lyx-gen -c IEEEtran --preamble '\input{tex/preamble.tex}' -p 'rc_proposal_*.lyx' -o $@
#dptr1_*.lyx

include commons/make/latex.mk
include commons/make/lyx.mk


# # include commons/make/bibtricks.mk
# # include commons/make/attach.mk

# sub:
# 	$(MAKE) -B clean dptr1b.tex
# 	pdflatex dptr1b_final
# 	pdflatex dptr1b_final 
# 	bibtex dptr1b_final
# 	pdflatex dptr1b_final
# 	bibtex dptr1b_final
# 	bibtex dptr1b_final
# 	pdflatex dptr1b_final
# 	pdflatex dptr1b_final