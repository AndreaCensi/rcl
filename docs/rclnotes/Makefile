
lyx_files=rclnotes.lyx

.PHONY: all

all:: rclnotes.pdf


rclnotes.lyx: 
	lyx-gen -c IEEEtran --preamble '\input{tex/preamble.tex}' -p 'rclnotes_*.lyx' -o $@
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