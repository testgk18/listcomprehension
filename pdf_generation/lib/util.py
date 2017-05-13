"""
A few library functions for pdf generation via python + LaTeX
"""

import PyPDF2
import os
import shutil
import time
import subprocess

def read_template(file_name):
  """reads the tex content from a file and returns it as a string"""
 
  # open file
  with open(file_name, 'r') as file:

    # skip lines until we read a latex comment marker
    for line in file:
      if len(line) > 0 and line[0] == '%': break

    # add lines to the template until we read a python docstring marker
    template = ""
    for line in file:
      if len(line) >= 3 and line[0:3] == '"""': break
      template += line

  # return template
  return template


def create_pdf(tex_doc, file_name, keep_tex=True):
  """
  renders a tex document as pdf

  tex_doc:    a string containing the TeX source
  file_name:  a string containing the output file name (without .pdf)
  keep_tex: a boolean indicating whether the tex file shall be kept
  """

  # create tex file
  with open(file_name + ".tex", 'w') as file:
    file.write(tex_doc)

  # generate pdf from tex file
  cmd = ['pdflatex', '-interaction', 'batchmode', file_name]
  proc = subprocess.Popen(cmd)
  proc.communicate()

  # check, if any latex errors
  retcode = proc.returncode
  if retcode != 0:

    # print error and halt
    raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd)))

  # eventually delete tex file
  if not keep_tex:
    os.remove(file_name + ".tex")


def create_pdf_series(template, args, variants):
  """
  creates a single pdf file, as a merged series of individualized templates.

  template: a string containing a TeX document with placeholders
  args:     a Namespace containing command line options such as the output file name
  variants: a generator that will produce the variants by replacing the placeholders
  """

  # we need a counter to name the temp PDF files
  counter = 0

  # Merger to collect the temp PDF files
  merger = PyPDF2.PdfFileMerger()

  # create temp directory
  temp_dir = "temp" + str(time.time())
  os.makedirs(temp_dir)
  os.chdir(temp_dir)

  # iterate on the variants
  for v in variants:

    # increment counter
    counter += 1

    # create pdf
    create_pdf(v, str(counter))

    # append temp file to merger
    merger.append(str(counter) + '.pdf')

  # CSV parsing complete
  # delete output file in case it exists
  if os.path.isfile(args.output):
    os.remove(args.output)

  # merge the pdf files, write the result and clean up
  os.chdir("..")
  with open(args.output, 'wb') as file:
    merger.write(file)
    shutil.rmtree(temp_dir)