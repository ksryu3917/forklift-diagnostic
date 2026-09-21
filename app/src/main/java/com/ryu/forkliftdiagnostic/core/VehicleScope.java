package com.ryu.forkliftdiagnostic.core;

public final class VehicleScope {
    public final String manufacturer;
    public final String model;
    public final String powertrain;

    public VehicleScope(String manufacturer, String model, String powertrain) {
        this.manufacturer = manufacturer;
        this.model = model;
        this.powertrain = powertrain;
    }

    public boolean exactMatches(String mfg, String mdl) {
        return manufacturer.equalsIgnoreCase(mfg) && model.equalsIgnoreCase(mdl);
    }
}
