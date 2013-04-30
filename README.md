lis_inspect
===========

Utility for inspecting/analyzing a flatfile in EPOCH's .lis format

The focus of this software is to provide a tool to do Python-based queries on a text file in the .lis format used by the EPOCH satellite ground system.  The semantic aspects of and EPOCH .lis file are separated from the overall parsing function, making it easy to add new semantic elements as necessary, or provide a parser for a different file that follows the same syntax.  See relevant sections below for a description of the .lis file syntax and a few of the EPOCH specifics.

Using lis_inspect
--------
lis_inspect is in theory capable of making any sort of query you might want into a .lis file, provided the elements involved in the query are all defined and have objects that sufficiently describe them, and provided Python code has been written, or can be written, to implement the query.

But most common use will be to find a "top-level element" (in EPOCH, a "point", "event", "global", etc.) that satisfies some criteria, for testing purposes.  For example, you may want to find a point that contains both states (indicated by children of type TLM_STATE_CONTEXT) and limits (children of type TLM_LIMITS_SET).  There are a variety of ways to do this, but let's start with the easiest.  For a simple query like this, it is convenient to use the inspect.py script, which will load the appropriate libraries, and then drop you into a Python prompt, where you can enter the appropriate query:

    $ ./inspect.py ~/lisfiles/cheapsat1/cheapsat1.lis 
       Do queries here.  Create functions to use as predicates to
       find_point, find_next_command, etc.

       Examples: 

          find_point(lambda p: len(p.children.get('TLM_LIMITS_SET') or []) > 1)

          find_next_point(location_lambda(115))
    >>> p = find_point(lambda p: p.children.get('TLM_LIMITS_SET') and p.children.get('TLM_STATE_CONTEXT'))
    Match found: AAA
    >>> ^D

The .lis file
-------------

The EPOCH satellite ground system uses flat files to describe the telemetry and commanding of a particular satellite, as well as ground system parameters and event message definitions to be used in the operation of the satellite.

In general terms, the file format appears as follows:

    [TOP_LEVEL_TYPE1] KEY1 VALUE1 KEY2 "VALUE 2" KEY3 VALUE3 ;;
      KEY4 VALUE4
      # Comments look like this
      [CHILD_NODE_TYPE1] KEY1 VALUE1 ;; #Continuation character
          KEY2 "VALUE2"
      # There may be more than one child node of the same type, depending on the type
      [CHILD_NODE_TYPE1] KEY1 VALUE3 ;; 
          KEY2 "VALUE4"
      [CHILD_NODE_TYPE2] KEY1 VALUE1
          [SUBCHILD_NODE] KEY1 VALUE1
          [SUBCHILD_NODE] KEY2 VALUE2
          
    [TOP_LEVEL_TYPE1] KEY1 VALUE5
       # etc....
       
    [TOP_LEVEL_TYPE2] KEY1 VALUE1
       [CHILD_NODE_TYPE3] KEY1 VALUE1
       # etc....
       
This format is somewhat analogous to XML, in that we have elements, which can have child elements as well as attributes.  It differs from XML, however, in that there is no syntactical way to determine the relationship between elements.  In XML, each element must be closed with a closing tag.  So if you see

    <foo><bar></bar></foo>
    
You know 'bar' is a child of 'foo' by looking at the syntactical relationship between the tags.  With the .lis format, however, there are no closing tags, nor is indentation significant.  The relationship between the nodes in practice must be hardcoded into the parser.
