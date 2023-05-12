# Example Host Tools
The host tools are split into four following files that may be of interest.
These host tools implement an example of how to utilize the required functionality:

* `enable_tool`: Implements sending a packaged feature to a fob
* `package_tool`: Implements creating a packaged feature
    - dependencies: 
        - word.h, permutations.h, ascon.h - Implements encryption scheme
        - package_feature.c - Implements code to encrypt the package
* `unlock_tool`: Listens for unlock messages from the car while unlocking via button
* `pair_tool`: Implements pairing an unpaired fob through a paired fob

