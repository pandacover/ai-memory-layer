type BrandMarkProps = {
  status: string;
};

export function BrandMark({ status }: BrandMarkProps) {
  return (
    <div className="floating-mark" aria-hidden="true">
      <span>ΜΝ</span>
      <b>Oracle</b>
      <em>{status}</em>
    </div>
  );
}
