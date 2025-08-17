import React from "react";
import { Card, Statistic } from "antd";

interface StatCardProps {
  title: string;
  value: number | string;
  prefix?: React.ReactNode;
  suffix?: React.ReactNode | string;
  color?: string;
  precision?: number;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  prefix,
  suffix,
  color,
  precision,
}) => {
  return (
    <Card size="small">
      <Statistic
        title={title}
        value={value as any}
        prefix={prefix}
        suffix={suffix}
        precision={precision}
        valueStyle={color ? { color } : undefined}
      />
    </Card>
  );
};

export default StatCard;