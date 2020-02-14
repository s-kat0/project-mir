# Base image
FROM python:3.7

# Run Commands
RUN pip install numpy
RUN pip install stanfordnlp

# Commands used when start container
CMD ["/bin/bash"]

CMD ["apt-get update"]
CMD ["apt-get install vim"]
CMD ["apt-get install emacs"]