
- resources
    - device manager
        - device discovery
        - initialize devices
            - prime the api
            - assign unique id

    - buffer manager
        - buffer for acquisition

    - device manager
    
    - driver manager
        - device primitives
            (DRIVER holds DEVICE PRIMITIVES, DEVICES are instantiated DEVICE PRIMITIVES)

- script
    - define execution relationship between devices in ONE ACQUISITION CYCLE
        - may use blockly to generate
    
- dispatcher
    - associate abstract devie requirement with actual devices from devicemanager
    - execute script
        - assign required parameters to devices
        - generate control sequence
            - may upload to sequencer

- acquisition
    - file io location
    - profile 
        - xy
            - region
            - tiles
        - z
            - layers
            - focus
        - c
            - channels
        - t
            - repeats
            - intervals
            - exposure

---

driver -> device (virtual) -> hardware (physical)