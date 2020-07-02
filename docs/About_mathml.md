This document explains Mathematical Markup Language (MathML) and tells you tags used in MathML.<br>
This documents help you to understand the code "xmldocument.py", which extracts formulae in scientific texts.


## Presentation Markup
p. 30
> 3.1.3.1  _Inferred \<mrow\>s_
>
> The elements listed in the following table as requiring 1* argument (msqrt, mstyle, merror, mpadded, mphantom, menclose, mtd, mscarry, and math) conceptually accept a single argument, but actually accept any number of children. If the number of children is 0 or is more than 1, they treat their contents as a single inferred mrow formed from all their children, and treat this mrow as the argument.
>
> For example,
>
> \<mtd\>\</mtd\>
>
> is treated as if it were
>
> \<mtd\> \<mrow\> \</mrow\>\</mtd\>




Thus, all of the elements are arguments of _mrow_ element.



p. 31
> Table of argument requirements

| Element       | Required argument count | Argument roles (when these differ by position)                                |
| ------------- | ----------------------- | ----------------------------------------------------------------------------- |
| mrow          | 0 or more               |                                                                               |
| mfrac         | 2                       | numerator denominator                                                         |
| msqrt         | 1                       |                                                                               |
| mroot         | 2                       | base index                                                                    |
| mstyle        | 1                       |                                                                               |
| merror        | 1                       |                                                                               |
| mpadded       | 1                       |                                                                               |
| mphantom      | 1                       |                                                                               |
| mfenced       | 0 or more               |                                                                               |
| menclose      | 1                       |                                                                               |
| msub          | 2                       | base subscript                                                                |
| msup          | 2                       | base superscript                                                              |
| msubsup       | 3                       | base subscript superscript                                                    |
| munder        | 2                       | base underscript                                                              |
| mover         | 2                       | base overscript                                                               |
| munderover    | 3                       | base underscript overscript                                                   |
| mmultiscripts | 1 or more               | base (subscript superscript) [\<mprescripts/\> (presubscript presuperscript)] |
| mtable        | 0 or more rows          | 0 or more mtr or mlabeledtr elements                                          |
| mlabeledtr    | 1 or more               | a label and 0 or more mtd elements                                            |
| mtr           | 0 or more               | 0 or more mtd elements                                                        |
| mtd           | 1                       |                                                                               |
| mstack        | 0 or more               |                                                                               |
| mlongdiv      | 3 or more               | divisor result divided (msrow \| msgroup \| mscarries \| msline)              |
| msgroup       | 0 or more               |                                                                               |
| msrow         | 0 or more               |                                                                               |
| mscarries     | 0 or more               |                                                                               |
| mscarry       | 1                       |                                                                               |
| maction       | 1 or more               | depend on actiontype attribute                                                |
| math          | 1                       |                                                                               |

p. 37
> Summary of Presentaion Elements
#### 3.1.9.1 Token Elements
| Element | Description                   |
| ------- | ----------------------------- |
| mi      | identifier                    |
| mn      | number                        |
| mo      | operator, fence, or separator |
| mtext   | text                          |
| mspace  | space                         |
| ms      | string literal                |


#### 3.1.9.2 General Layout Schemata
| Element  | Description                                                            |
| -------- | ---------------------------------------------------------------------- |
| mrow     | group any number of sub-expressions horizontally                       |
| mfrac    | form a fraction from two sub-expressions                               |
| msqrt    | form a square root (radical without an index)                          |
| mroot    | form a radical with specified index                                    |
| mstyle   | style change                                                           |
| merror   | enclose a syntax error message from a preprocessor                     |
| mpadded  | adjust space around context                                            |
| mphantom | make content invisible but preserve its size                           |
| mfenced  | surround content with a pair of fences                                 |
| menclose | enclose content with a stretching symbol such as a long division sign. |


#### 3.1.9.3 Script and Limit Schemata
| Element       | Description                                     |
| ------------- | ----------------------------------------------- |
| msub          | attach a subscript to a base                    |
| msup          | attach a superscript to a base                  |
| msubsup       | attach a subscript-superscript pair to a base   |
| munder        | attach an underscript to a base                 |
| mover         | attach an overscript to a base                  |
| munderover    | attach an underscript-overscript pair to a base |
| mmultiscripts | attach prescripts and tensor indices to a base  |


#### 3.1.9.4 Tables and Matrices
| Element                    | Description                                              |
| -------------------------- | -------------------------------------------------------- |
| mtable                     | table or matrix                                          |
| mlabeledtr                 | row in a table or matrix with a label or equation number |
| mtr                        | row in a table or matrix                                 |
| mtd                        | one entry in a table or matrix                           |
| maligngroup and malignmark | alignment markers                                        |


#### 3.1.9.5 Elementary Math Layout
| Element   | Description                                                       |
| --------- | ----------------------------------------------------------------- |
| mstack    | columns of aligned characters                                     |
| mlongdiv  | similar to msgroup, with the addition of a divisor and result     |
| msgroup   | a group of rows in an mstack that are shifted by similar amoutnts |
| msrow     | a row in an mstack                                                |
| mscarries | row in an mstack that whose contents represent carries or borrows |
| mscarry   | oen entry in an mscarries                                         |
| msline    | horizontal line inside of mstack                                  |


#### 3.1.9.6 Enlivening Expressions
| Element | Description                      |
| ------- | -------------------------------- |
| maction | bind actions to a sub-expression |





### Reference
[Mathematical Markup Language (MathML) Version 3.0 2nd Edition, Chapter 3 Presentation Markup](https://www.w3.org/TR/MathML3/mathml.pdf)


