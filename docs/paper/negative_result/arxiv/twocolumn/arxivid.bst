% Minimal BibTeX style: prints the reference list as the manuscript writes it,
% "Author. Title (note). [arXiv:id, year; venue]" with numeric labels, in order of first citation (no sorting, no case changes).
ENTRY { author title eprint note year venue bracket } { } { }

FUNCTION {misc}
{ "\bibitem{" cite$ * "}" * write$
  newline$
  author #-1 #1 substring$ "." =
    { author " " * }
    { author ". " * }
  if$
  title *
  note empty$
    { "." * }
    { " (" * note * ")." * }
  if$
  bracket empty$
    { " [arXiv:" * eprint * ", " * year *
      venue empty$
        { "]" * }
        { "; " * venue * "]" * }
      if$
    }
    { " [" * bracket * "]" * }
  if$
  write$
  newline$
}

FUNCTION {begin.bib}
{ "\begin{thebibliography}{99}" write$
  newline$
}

FUNCTION {end.bib}
{ newline$
  "\end{thebibliography}" write$
  newline$
}

READ
EXECUTE {begin.bib}
ITERATE {call.type$}
EXECUTE {end.bib}
