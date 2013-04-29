lis_inspect
===========

Utility for finding ispecting/analyzing a flatfile in EPOCH's .lis format

The EPOCH satellite ground system uses flat files to describe the telemetry and commanding of a particular satellite, as well as ground system parameters and event message definitions to be used in the operation of the satellite.

In general terms, the file format appears as follows:

    [TOP_LEVEL_TYPE1] KEY1 VALUE1 KEY2 "VALUE 2" KEY3 VALUE3 ;;
      KEY4 VALUE4
      # Comments look like this
      [CHILD_NODE_TYPE1] KEY1 VALUE1 ;; #Continuation character
          KEY2 "VALUE2"
      # There may be more than one chile node of the same type, depending on the type
      [CHILD_NODE_TYPE1] KEY1 VALUE3 ;; 
          KEY2 "VALUE4"
      [CHILD_NODE_TYPE2] KEY1 VALUE1
          [SUBCHILD_NODE] KEY1 VALUE1
          [SUBCHILD_NODE] KEY2 VALUE2
          
    [TOP_LEVEL_TYPE1] KEY1 VALUE3
       # etc....
       
    [TOP_LEVEL_TYPE2] KEY1 VALUE1
       [CHILD_NODE_TYPE3] KEY1 VALUE1
       # etc....
       
This format is somewhat analogous to XML, in that we have elements, which can have child elements as well as attributes.  It differs from XML, however, in that there is no syntactical way to determine the relationship between elements.  In XML, each element must be closed with a closing tag.  So if you see

    <foo><bar></bar></foo>
    
You know 'bar' is a child of 'foo' by looking at the syntactical relationship between the tags.  With the .lis format, however, there are no closing tags, nor is indentation significant.  The relationship between the nodes in practice must be hardcoded into the parser.
