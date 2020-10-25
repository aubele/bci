ALL: posterDeepLearning.pdf posterHomeAutomation.pdf

%.pdf: %.tex Makefile
	pdflatex --enable-write18 $< &&	pdflatex $< && pdflatex $<

clean:
	  rm -f *.aux	*.bbl	*.blg	*.log
