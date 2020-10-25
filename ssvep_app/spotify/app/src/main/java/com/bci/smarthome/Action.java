package com.bci.smarthome;

/**
 * Action class, which is used to create action objects with a unique id and a label which can
 * be changed later
 * the id should always be unique, it is mainly used to allow sorting
 * the label is used for displaying a text above the boxes
 * implements comparable to allow sorting in a treemap
 */
public class Action implements Comparable<Action> {

    private String label;
    private int id;

    public Action(String label, int id) {
        this.label = label;
        this.id = id;
    }

    public String getLabel() {
        return label;
    }
    public void setLabel(String label) {
        this.label = label;
    }
    public int getId() {
        return id;
    }

    @Override
    public int compareTo(Action act) {
        int ret = 0;
        if(this.getId() == act.getId()){
            ret = 0;
        } else if(act.getId() > this.getId()) {
            ret = -1;
        } else if(this.getId() > act.getId()) {
            ret = 1;
        }
        return ret;
    }
}
