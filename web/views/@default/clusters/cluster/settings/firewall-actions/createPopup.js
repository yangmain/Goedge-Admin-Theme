Tea.context(function () {
    this.$delay(function () {
        let that = this

        // 类型
        this.$watch("type", function () {
            that.changeType()
        })

        this.changeType()
    })

    /**
     * 类型
     */
    this.type = ""
    this.typeDescription = ""

    this.changeType = function () {
        let that = this
        let t = this.actionTypes.$find(function (k, v) {
            return v.code == that.type
        })
        if (t != null) {
            this.typeDescription = t.description
        } else {
            this.typeDescription = ""
        }
    }
})