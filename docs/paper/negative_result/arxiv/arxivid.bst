% Minimal BibTeX style: prints the reference list as the manuscript writes it,
% "[arXiv id] Author. Title (note).", in the order of the .bib file (no sorting, no case changes).
ENTRY { author title eprint note } { } { }

FUNCTION {misc}
{ "\bibitem[" eprint * "]{" * cite$ * "}" * write$
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
  write$
  newline$
}

FUNCTION {begin.bib}
{ "\begin{thebibliography}{2406.13352}" write$
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
