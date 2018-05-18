# RTDMTD algorithm

I implemented the algorithm in this paper using Beautifulsoup:

http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.105.629&rep=rep1&type=pdf
    
    
These are the steps in the algorithm:
- Guiven 2 pages A and B, use the DOM of the pages to represent them as trees.
- Find the edition between the 2 pages with minimal cost. The possible tree editions are: insertion, deletion or replace
- The nodes that are keep intact in the edition with minimal cost are considered template nodes. 
Create the minimal subtree containing that nodes. This subtree is the template.
